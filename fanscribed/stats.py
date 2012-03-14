"""Stats generator for Fanscribed."""

import argparse
from cgi import escape
import cPickle as pickle
from collections import namedtuple
from datetime import datetime
from hashlib import sha1
from operator import itemgetter
import os
import sys
from urllib2 import quote

from ujson import load

import git

from twiggy import log, quickSetup


# TODO: Read from config file or command line.
LOCK_TIMEOUT = 20 * 60


def get_parser():
    parser = argparse.ArgumentParser(
        description='Generate Fanscribed statistics.',
    )
    parser.add_argument(
        'repos',
        metavar='REPO',
        type=str,
        nargs='+',
        help='a repository to generate stats from',
    )
    parser.add_argument(
        '--pickle', '-p',
        metavar='FILENAME',
        type=str,
        nargs=1,
        required=False,
        default=None,
        help='pickle file in which to cache stats',
    )
    parser.add_argument(
        '--output-path', '-o',
        metavar='PATH',
        type=str,
        nargs=1,
        required=True,
        help='directory to write stats results to',
    )
    parser.add_argument(
        '--email-map', '-m',
        metavar='FROM:TO',
        type=str,
        nargs='*',
        required=False,
        help='Map one email address to another',
    )
    parser.add_argument(
        '--email-ignore', '-i',
        metavar='EMAIL',
        type=str,
        nargs='*',
        required=False,
        help='Ignore an email address',
    )
    return parser


class _SimpleObject(object):

    __slots__ = []

    def __init__(self, **kwargs):
        # Initialize based on kwargs, or None if value not given.
        for name in self.__slots__:
            setattr(self, name, kwargs.get(name, None))


class AuthorInfo(_SimpleObject):

    __slots__ = [
        'names',  # set()
        'locks_created',  # dict(reponame={secret:Lock(), ...})
        'snippets',  # dict(reponame={
                     #     starting_point: [
                     #         SnippetAction(), ...
                     #     ],
                     # })
        'total_actions',  # int
        'total_transcriptions',  # int
        'total_bytes_transcribed',  # int
        'time_spent',  # float
        'time_spent_transcribing',  # float
        'average_time_per_transcription',  # float
        'average_wpm',  # float
    ]


class Lock(_SimpleObject):

    __slots__ = [
        'type',  # 'review' or 'snippet'
        'starting_point',  # ms
        'timestamp',  # time
        'created_at',  # time
        'created_by',  # email
        'destroyed_at',  # time
        'destroyed_by',  # email
        'snippet_created',  # bool  TODO
        'snippet_updated',  # bool  TODO
    ]


class RepoInfo(_SimpleObject):

    __slots__ = [
        'name',  # str
        'transcription',  # dict
        'authors',  # set()
        'snippets',  # {starting_point: [SnippetAction(), ...]}
    ]

    @property
    def repo(self):
        return git_repos_by_name[self.name]


class SnippetAction(_SimpleObject):
    """Represents the creation or modification of a snippet."""

    __slots__ = [
        'email',  # str
        'saved',  # time
        'bytes',  # int
    ]

    def __cmp__(self, other):
        return cmp((self.saved, self.email), (other.saved, other.email))


# Map author emails to stats.
authors_map = {
    # email: AuthorInfo(),
}


review_locks = {
    # secret: Lock(),
}


snippet_locks = {
    # secret: Lock(),
}


# Map repo path to repo.
repo_infos_by_path = {
    # path: RepoInfo(),
}
repo_infos_by_name = {
    # name: RepoInfo(),
}
git_repos_by_name = {
    # name: git.Repo(),
}


# Keep information on the last commit processed in each repo.
latest_commits = {
    # name: last_commit,
}


email_maps = {
    # email-from: email-to,
}
email_ignores = set([
    # email,
])


def main():
    # Parse options and ensuring existence of input and output paths.
    quickSetup()
    parser = get_parser()
    options = parser.parse_args()
    if options.pickle is not None:
        options.pickle = options.pickle[0]  # list -> string
        unpickle_all(options.pickle)
    else:
        # Do nothing; keep initial state.
        pass
    if options.email_map:
        for email_mapping in options.email_map:
            email_from, email_to = email_mapping.split(':')
            email_maps[email_from] = email_to
            log.fields(email_from=email_from, email_to=email_to).info('email mapping')
    if options.email_ignore:
        email_ignores.update(options.email_ignore)
    output_path = options.output_path[0]
    pathlog = log.fields(output_path=output_path)
    if os.path.isdir(output_path):
        pathlog.info('directory OK')
    elif os.path.exists(output_path):
        pathlog.error('is NOT a directory')
        sys.exit(1)
    else:
        pathlog.error('does NOT exist')
        sys.exit(1)
    all_repos_valid = True
    for repo_path in options.repos:
        repolog = log.fields(repo_path=repo_path)
        try:
            repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            repolog.error('is NOT a repository')
            all_repos_valid = False
        except git.NoSuchPathError:
            repolog.error('does NOT exist')
            all_repos_valid = False
        else:
            repolog.info('repository OK')
            tree = repo.tree('master')
            transcription_json = load(tree['transcription.json'].data_stream)
            repo_name = os.path.split(repo_path)[-1]
            git_repos_by_name[repo_name] = repo
            if repo_path not in repo_infos_by_path:
                # Create new RepoInfo structure.
                repo_infos_by_path[repo_path] = repo_infos_by_name[repo_name] = RepoInfo(
                    name=repo_name,
                    transcription=transcription_json,
                    authors=set(),
                    snippets={},
                )
            else:
                # Keep existing RepoInfo structure.
                pass
    if not all_repos_valid:
        sys.exit(1)
    process_all_repos()
    process_all_authors()
    create_all_output(output_path)
    if options.pickle is not None:
        pickle_all(options.pickle)


# ===================================================================
# pickling


def pickle_all(filename, log=log):
    log.fields(filename=filename).info('pickling')
    structure = dict(
        authors_map=authors_map,
        review_locks=review_locks,
        snippet_locks=snippet_locks,
        latest_commits=latest_commits,
        repo_infos_by_path=repo_infos_by_path,
        repo_infos_by_name=repo_infos_by_name,
    )
    with open(filename, 'wb') as f:
        pickle.dump(structure, f, -1)


def unpickle_all(filename, log=log):
    log = log.fields(filename=filename)
    if os.path.isfile(filename):
        log.info('unpickling')
        with open(filename, 'rb') as f:
            globals().update(pickle.load(f))
    else:
        log.info('notfound')


# ===================================================================
# processing


def normalize_email(email):
    """Strip; lowercase; replace foo+bar@gmail.com with foo@gmail.com"""
    email = email.strip().lower()
    # Replace with mapped email if it exists; otherwise use given email.
    email = email_maps.get(email, email)
    return email


def process_all_repos():
    """Loop through events in all repositories."""
    for repo_path, repo_info in repo_infos_by_path.iteritems():
        repo = repo_info.repo
        repo_name = repo_info.name
        repolog = log.fields(repo_name=repo_name)
        repolog.info('processing')
        last_locks = {}
        prev_latest_commit = latest_commits.get(repo_name, None)
        if prev_latest_commit is not None:
            repolog.fields(prev_latest_commit=prev_latest_commit).info()
        else:
            repolog.info('new repo')
        latest_commit = repo.commit('master').hexsha
        commits = []
        # Find applicable commits.
        for commit in repo.iter_commits(latest_commit):
            if commit.hexsha == prev_latest_commit:
                # Reached commit we stopped at last time.
                break
            else:
                commits.append(commit)
        # Process them starting with eldest first.
        for commit in reversed(commits):
            email = normalize_email(commit.author.email)
            update_authors_map(email, commit)
            last_locks = update_locks(email, repo_name, commit, last_locks)
            update_snippets(email, repo_info, commit)
        # Store latest commit for next time.
        latest_commits[repo_name] = latest_commit
        repolog.fields(latest_commit=latest_commit).info()


def process_all_authors():
    """Loop through authors to calculate author-specific stats."""
    for author_info in authors_map.itervalues():
        author_log = log.fields(author_name=sorted(author_info.names)[0])
        author_log.info('processing')
        # Reset accumulators.
        author_info.total_actions = 0
        author_info.total_transcriptions = 0
        author_info.time_spent = 0
        author_info.time_spent_transcribing = 0
        author_info.total_bytes_transcribed = 0
        # Process snippets.
        for repo_name, snippet_map in author_info.snippets.iteritems():
            for starting_point, snippet_actions in snippet_map.iteritems():
                author_info.total_actions += len(snippet_actions)
                # Determine if the snippet action was a transcription.
                repo_info = repo_infos_by_name[repo_name]
                first_repo_snippet_action = repo_info.snippets[starting_point][0]
                if first_repo_snippet_action in snippet_actions:
                    author_info.total_transcriptions += 1
        # Process locks.
        for repo_name, locks_map in author_info.locks_created.iteritems():
            for lock in locks_map.itervalues():
                if lock.created_by == lock.destroyed_by:
                    duration = lock.destroyed_at - lock.created_at
                    author_info.time_spent += duration
                    # Determine if the lock was associated with a transcription, vs. an edit.
                    repo_info = repo_infos_by_name[repo_name]
                    if lock.starting_point in repo_info.snippets:
                        first_repo_snippet_action = repo_info.snippets[lock.starting_point][0]
                        if first_repo_snippet_action.saved == lock.destroyed_at:
                            author_info.time_spent_transcribing += duration
                            author_info.total_bytes_transcribed += first_repo_snippet_action.bytes
        if author_info.total_transcriptions:
            author_info.average_time_per_transcription = author_info.time_spent_transcribing / author_info.total_transcriptions
            author_info.average_wpm = (author_info.total_bytes_transcribed / 5.0) / (author_info.time_spent_transcribing / 60.0)


def update_authors_map(email, commit):
    """Update the authors map based on the given commit."""
    author = commit.author
    if email not in authors_map:
        authors_map[email] = AuthorInfo(
            names=set(),
            locks_created=dict(),
            snippets=dict(),
            total_actions=0,
            total_transcriptions=0,
            total_bytes_transcribed=0,
            time_spent=0.0,
            time_spent_transcribing=0.0,
            average_time_per_transcription=0.0,
            average_wpm=0.0,
        )
    author_info = authors_map[email]
    author_info.names.add(author.name)


RotatedLock = namedtuple('RotatedLock', 'starting_point timestamp')


def update_locks(email, repo_name, commit, last_locks):
    """Update locks based on the given commit."""
    tree = commit.tree
    author_info = authors_map[normalize_email(email)]
    date = commit.authored_date
    if 'locks.json' in tree:
        locks = load(tree['locks.json'].data_stream)
        for lock_type, locks_dict in [
            ('snippet', snippet_locks),
            ('review', review_locks),
        ]:
            # Snippets.
            this_locks = locks.get(lock_type, {})
            last_locks = last_locks.get(lock_type, {})
            this_by_secret = dict(
                (
                    value['secret'],
                    RotatedLock(starting_point=int(key), timestamp=value['timestamp']),
                )
                for key, value
                in this_locks.iteritems()
            )
            last_by_secret = dict(
                (
                    value['secret'],
                    RotatedLock(starting_point=int(key), timestamp=value['timestamp']),
                )
                for key, value
                in last_locks.iteritems()
            )
            removed_secrets = set(last_by_secret) - set(this_by_secret)
            added_secrets = set(this_by_secret) - set(last_by_secret)
            for secret in removed_secrets:
                lock = locks_dict.get(secret)
                if lock is not None:
                    updated_lock = locks_dict[secret]
                    updated_lock.destroyed_at = date
                    updated_lock.destroyed_by = email
            for secret in added_secrets:
                this = this_by_secret[secret]
                locks_dict[secret] = new_lock = Lock(
                    type=lock_type,
                    starting_point=int(this.starting_point),
                    timestamp=this.timestamp,
                    created_at=date,
                    created_by=email,
                )
                author_repo_locks_created = author_info.locks_created.setdefault(repo_name, {})
                author_repo_locks_created[secret] = new_lock
        # Pass along most recently-read locks to compare with next round.
        return locks
    else:
        # Pass along last used locks to compare with next round, since
        # the structure wasn't found in the repo.
        return last_locks


def update_snippets(email, repo_info, commit):
    """Update information about snippets touched by a commit."""
    repo_name = repo_info.name
    repo_snippets = repo_info.snippets
    author_info = authors_map[email]
    for filename in commit.stats.files:
        if len(filename) == 20 and filename.endswith('.txt'):
            # It's a snippet.  Find its starting point and create a SnippetAction instance.
            starting_point = int(filename[:16])
            snippet_action = SnippetAction(
                email=email,
                saved=commit.authored_date,
                bytes=commit.tree[filename].size if filename in commit.tree else 0,
            )
            # Add the snippet change to the author's info.
            author_repo_snippets = author_info.snippets.setdefault(repo_name, {})
            author_repo_snippets_list = author_repo_snippets.setdefault(starting_point, [])
            author_repo_snippets_list.append(snippet_action)
            # Add the snippet change to the repo's info.
            repo_snippets_list = repo_snippets.setdefault(starting_point, [])
            repo_snippets_list.append(snippet_action)


# ===================================================================
# output


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html>
    <head>
        <title>{head_title} - Stats - Fanscribed</title>
        <style type="text/css">
            #footer {{
                font-style: italic;
                border-top: thin solid black;
            }}
        </style>
    </head>
    <body>
        {index_link}
        <h1>{title}</h1>
        <div>
            {body}
        </div>
        <div id="footer">
            Generated at {timestamp}.
        </div>
    </body>
</html>
"""


def ms_to_label(ms):
    seconds = ms / 1000
    minutes = seconds / 60
    seconds %= 60
    return '{0:d}m{1:02d}s'.format(minutes, seconds)


def snippets_in_ms(ms, per_snippet=30000):
    """Return the number of snippets possible in the given number of milliseconds."""
    snippets_total = ms / per_snippet
    if ms % per_snippet:
        # There is a partial snippet at the end.
        snippets_total += 1
    return snippets_total


def author_names(info):
    return u', '.join(sorted(info.names))


def author_filename(email):
    return 'author_{0}.html'.format(sha1(email).hexdigest())


def transcript_filename(name):
    return 'transcript_{0}.html'.format(name)


def create_all_output(path):
    create_index(path)
    create_all_transcript_pages(path)
    create_all_author_pages(path)


def create_index(path):
    body = ''
    # Transcripts.
    # ------------
    transcripts_list = [
        # (name, html),
    ]
    for repo_path, repo_info in repo_infos_by_path.iteritems():
        name = repo_info.name
        url = transcript_filename(name)
        transcripts_list.append((
            name,
            '<li><a href="{url}">{name}</a></li>'.format(
                url=quote(url),
                name=name,
            ),
        ))
    # Sort by name.
    transcripts_list.sort(key=itemgetter(0))
    body += """
        <h2>Transcripts</h2>
        <ul>
            {transcripts_list}
        </ul>
    """.format(
        transcripts_list='\n'.join(html for name, html in transcripts_list),
    )
    # Authors.
    # --------
    authors_list = [
        # (names, html),
    ]
    for email in sorted(authors_map):
        author_info = authors_map[email]
        if email not in email_ignores and author_info.total_actions:
            # Only include authors who have contributed at least one snippet.
            url = author_filename(email)
            names = escape(author_names(author_info))
            authors_list.append((
                names,
                author_info.time_spent,
                author_info.total_transcriptions,
                author_info.average_wpm,
                '<li><a href="{url}">{names}</a> ({time_spent:0.02f}h{speed})</li>'.format(
                    url=url,
                    names=names,
                    time_spent=author_info.time_spent / 60.0 / 60.0,
                    speed=', {total_transcriptions:d} @ ~ {average_wpm:0.02f} wpm'.format(
                        average_wpm=author_info.average_wpm,
                        total_transcriptions=author_info.total_transcriptions,
                    ) if author_info.total_transcriptions > 0 else '',
                ),
            ))
    # Sort by names, not by email address.
    authors_by_name = sorted(authors_list, key=lambda item: item[0].lower())
    # Sort by total time spent transcribing and editing.
    authors_by_time_spent = reversed(sorted(authors_list, key=lambda item: item[1]))
    # Sort by total # of transcriptions created.
    authors_by_total_transcriptions = reversed(sorted(
        [item for item in authors_list if item[2] > 0],  # exclude non-transcribers
        key=lambda item: item[2],
    ))
    # Sort by average WPM during transcription.
    authors_by_average_time = reversed(sorted(
        [item for item in authors_list if item[2] > 0],  # exclude non-transcribers
        key=lambda item: item[3],
    ))
    body += """
        <hr/>
        <p>Key: [author name] ([total hours spent], [transcriptions] @ [average <a href="http://en.wikipedia.org/wiki/Words_per_minute">WPM</a>])</p>
        <table border="0" cellspacing="10">
            <tr valign="top">
                <td>
                    <h2>Authors, by name</h2>
                    <ul>
                        {authors_by_name}
                    </ul>
                </td>
                <td>
                    <h2>Authors, by time spent</h2>
                    <ol>
                        {authors_by_time_spent}
                    </ol>
                </td>
            </tr>
            <tr valign="top">
                <td>
                    <h2>Authors, by transcriptions</h2>
                    <ol>
                        {authors_by_total_transcriptions}
                    </ol>
                </td>
                <td>
                    <h2>Authors, by average WPM</h2>
                    <ol>
                        {authors_by_average_time}
                    </ol>
                </td>
            </tr>
        </table>
    """.format(
        authors_by_time_spent='\n'.join(item[-1] for item in authors_by_time_spent),
        authors_by_name='\n'.join(item[-1] for item in authors_by_name),
        authors_by_total_transcriptions='\n'.join(item[-1] for item in authors_by_total_transcriptions),
        authors_by_average_time='\n'.join(item[-1] for item in authors_by_average_time),
    )
    write_page(
        index=True,
        path=path,
        filename='index.html',
        title='Fanscribed Stats',
        body=body,
    )


def create_all_transcript_pages(path):
    for repo_path, repo_info in repo_infos_by_path.iteritems():
        name = repo_info.name
        filename = transcript_filename(name)
        body = ''
        # General stats.
        # ==============
        body += '<h2>General stats</h2>'
        total_snippets = snippets_in_ms(repo_info.transcription['duration'])
        total_reviews = total_snippets - 1
        repo = repo_info.repo
        master = repo.tree('master')
        remaining_reviews = len(load(master['remaining_reviews.json'].data_stream))
        remaining_snippets = len(load(master['remaining_snippets.json'].data_stream))
        snippets_completed = total_snippets - remaining_snippets
        reviews_completed = total_reviews - remaining_reviews
        percent_reviews = (reviews_completed * 100) / total_reviews
        percent_snippets = (snippets_completed * 100) / total_snippets
        body += """
        <dl>
            <dt>Snippets transcribed</dt>
            <dd>{snippets_completed} of {total_snippets} ({percent_snippets}%)</dd>

            <dt>Reviews completed</dt>
            <dd>{reviews_completed} of {total_reviews} ({percent_reviews}%)</dd>
        </dl>
        """.format(**locals())
        # Authors and editors
        # ========
        # Figure out who the top transcriptionists and editors are.
        snippet_creators = {
            # email: [starting_point, ...],
        }
        snippet_editors = {
            # email: [starting_point, ...],
        }
        for starting_point, snippet_actions in repo_info.snippets.iteritems():
            transcriptionist = snippet_actions[0].email
            snippet_creator_snippets = snippet_creators.setdefault(transcriptionist, [])
            snippet_creator_snippets.append(starting_point)
            for snippet_action in snippet_actions[1:]:
                editor = snippet_action.email
                snippet_editor_snippets = snippet_editors.setdefault(editor, [])
                snippet_editor_snippets.append(starting_point)
        # Reverse sort by number of snippets created or edited.
        snippet_creators = reversed(sorted(snippet_creators.iteritems(), key=lambda kv: len(kv[1])))
        snippet_editors = reversed(sorted(snippet_editors.iteritems(), key=lambda kv: len(kv[1])))
        snippet_creators = [
            '<li><a href="{url}">{names}</a> ({count} snippets transcribed)</li>'.format(
                url=author_filename(email),
                names=author_names(authors_map[email]),
                count=len(starting_points),
            )
            for email, starting_points
            in snippet_creators
            if email not in email_ignores
        ]
        snippet_editors = [
            '<li><a href="{url}">{names}</a> ({count} snippets edited)</li>'.format(
                url=author_filename(email),
                names=author_names(authors_map[email]),
                count=len(starting_points),
            )
            for email, starting_points
            in snippet_editors
            if email not in email_ignores
        ]
        body += """
            <table border="0" cellspacing="10">
                <tr valign="top">
                    <td>
                        <h2>Top transcriptionists</h2>
                        <ol>
                            {snippet_creators}
                        </ol>
                    </td>
                    <td>
                        <h2>Top reviewers/editors</h2>
                        <ol>
                            {snippet_editors}
                        </ol>
                    </td>
                </tr>
            </table>
        """.format(
            snippet_creators='\n'.join(snippet_creators),
            snippet_editors='\n'.join(snippet_editors),
        )
        write_page(
            path=path,
            filename=filename,
            head_title='Transcript: {name}'.format(name=name),
            title='Transcript: <a href="http://{name}/">{name}</a>'.format(name=name),
            body=body,
        )


def create_all_author_pages(path):
    for email, author_info in authors_map.iteritems():
        names = escape(author_names(author_info))
        body = ''
        # General stats.
        body += """
            <h2>General stats</h2>
            <dl>
                <dt>Total transcribe/edit actions</td>
                <dd>{total_actions}</dd>

                <dt>Time spent transcribing/editing</td>
                <dd>{time_spent:0.02f} hours</dd>

                <dt>Total transcriptions</td>
                <dd>{total_transcriptions:d}</dd>

                <dt>Average <a href="http://en.wikipedia.org/wiki/Words_per_minute">words per minute</a></td>
                <dd>{average_wpm:0.02f} WPM</dd>
            </dl>
        """.format(
            total_actions=author_info.total_actions,
            time_spent=author_info.time_spent / 60.0 / 60.0,
            total_transcriptions=author_info.total_transcriptions,
            average_wpm=author_info.average_wpm,
        )
        # Snippets contributed to.
        body += '<h2>Snippets transcribed or edited</h2>'
        snippets_map = authors_map[email].snippets
        for repo_name in sorted(snippets_map):
            snippet_action_map = snippets_map[repo_name]
            starting_points = sorted(snippet_action_map)
            list_items = [
                '<li><a href="http://{repo_name}/#{label}">{repo_name}/#{label}</a></li>'.format(
                    repo_name=repo_name,
                    label=ms_to_label(starting_point)
                )
                for starting_point
                in starting_points
            ]
            body += """
                <h3>{repo_name}</h3>
                <ul>
                {list_items}
                </ul>
            """.format(
                repo_name=repo_name,
                list_items='\n'.join(list_items),
            )
        write_page(
            path=path,
            filename=author_filename(email),
            title='Author: {names}'.format(names=names),
            body=body,
        )


def write_page(path, filename, **kwargs):
    if 'index' not in kwargs:
        kwargs['index_link'] = '<p><a href="index.html">Back to stats home page</a></p>'
    else:
        kwargs['index_link'] = ''
    if 'head_title' not in kwargs:
        kwargs['head_title'] = kwargs['title']
    kwargs['timestamp'] = unicode(datetime.now())
    filename = os.path.join(path, filename)
    log.fields(filename=filename).info('writing')
    with open(filename, 'wb') as f:
        f.write(PAGE_TEMPLATE.format(**kwargs))
