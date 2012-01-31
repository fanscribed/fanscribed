"""Stats generator for Fanscribed."""

import argparse
from cgi import escape
from collections import namedtuple
from hashlib import sha1
from operator import attrgetter
import os
import sys
from ujson import load

import git
from twiggy import log, quickSetup


# TODO: Read from config file or command line.
LOCK_TIMEOUT = 20 * 60


def get_parser():
    parser = argparse.ArgumentParser(description='Generate Fanscribed statistics.')
    parser.add_argument(
        'repos',
        metavar='REPO',
        type=str,
        nargs='+',
        help='a repository to generate stats from',
    )
    parser.add_argument(
        '--output-path', '-o',
        metavar='PATH',
        type=str,
        nargs=1,
        required=True,
        help='directory to write stats results to',
    )
    return parser


secretgetter = attrgetter('secret')


class Lock(object):

    __slots__ = [
        'type',
        'starting_point',
        'timestamp',
        'created_at',
        'created_by',
        'destroyed_at',
        'destroyed_by',
    ]

    def __init__(self, **kwargs):
        # Initialize based on kwargs, or None if value not given.
        for name in self.__slots__:
            setattr(self, name, kwargs.get(name, None))


# Map author emails to stats.
authors_map = {
    # email: dict(
    #   names=set(),
    #   locks_created=dict(
    #       reponame=dict(
    #           secret=lock,
    #       ),
    #   ),
    # ),
}


review_locks = {
    # secret: Lock(),
}


snippet_locks = {
    # secret: Lock(),
}


# Map repo path to repo.
repos = {
    # path: Repo(),
}


def main():
    # Begin by parsing options and ensuring existence of input and output paths.
    quickSetup()
    parser = get_parser()
    options = parser.parse_args()
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
            repos[repo_path] = repo
    if not all_repos_valid:
        sys.exit(1)
    process_all_repos()
    create_all_output(output_path)


# ===================================================================
# processing


def process_all_repos():
    """Loop through events in all repositories."""
    for repo_path, repo in repos.iteritems():
        repo_name = os.path.split(repo_path)[-1]
        repolog = log.fields(repo_name=repo_name)
        repolog.info('processing')
        last_locks = {}
        for commit in reversed(list(repo.iter_commits('master'))):
            update_authors_map(commit)
            last_locks = update_locks(repo_name, commit, last_locks)


def update_authors_map(commit):
    """Update the authors map based on the given commit."""
    author = commit.author
    email = author.email.lower()
    if email not in authors_map:
        authors_map[email] = dict(
            names=set(),
            locks_created=dict(),
        )
    author_info = authors_map[email]
    author_info['names'].add(author.name)


RotatedLock = namedtuple('RotatedLock', 'starting_point timestamp')


def update_locks(repo_name, commit, last_locks):
    """Update locks based on the given commit."""
    tree = commit.tree
    email = commit.author.email
    author_info = authors_map[email.lower()]
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
                    RotatedLock(starting_point=key, timestamp=value['timestamp']),
                )
                for key, value
                in this_locks.iteritems()
            )
            last_by_secret = dict(
                (
                    value['secret'],
                    RotatedLock(starting_point=key, timestamp=value['timestamp']),
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
                    starting_point=this.starting_point,
                    timestamp=this.timestamp,
                    created_at=date,
                    created_by=email,
                )
                author_repo_locks_created = author_info['locks_created'].setdefault(repo_name, dict())
                author_repo_locks_created[secret] = new_lock
        # Pass along most recently-read locks to compare with next round.
        return locks
    else:
        # Pass along last used locks to compare with next round, since
        # the structure wasn't found in the repo.
        return last_locks


# ===================================================================
# output


PAGE_TEMPLATE = """\
<!DOCTYPE html>
<html>
    <head>
        <title>{title} - Stats - Fanscribed</title>
    </head>
    <body>
        <h1>{title}</h1>
        <div>
            {body}
        </div>
    </body>
</html>
"""


def author_names(info):
    return u', '.join(sorted(info['names']))


def author_filename(email):
    return 'author_{0}.html'.format(sha1(email).hexdigest())


def create_all_output(path):
    create_index(path)
    create_all_author_pages(path)


def create_index(path):
    body = ''
    # Authors.
    authors_list = [
        # (names, html),
    ]
    for email in sorted(authors_map):
        info = authors_map[email]
        url = author_filename(email)
        names = escape(author_names(info))
        authors_list.append((
            names,
            '<li><a href="{url}">{names}</a></li>'.format(
                url=url,
                names=names,
            ),
        ))
    # Sort by names, not by email address.
    authors_list.sort(key=lambda item: item[0].lower())
    body += """
        <h2>Authors</h2>
        <ul>
            {authors_list}
        </ul>
    """.format(
        authors_list='\n'.join(html for names, html in authors_list),
    )
    write_page(
        path=path,
        filename='index.html',
        title='Index',
        body=body,
    )


def create_all_author_pages(path):
    for email, info in authors_map.iteritems():
        names = escape(author_names(info))
        write_page(
            path=path,
            filename=author_filename(email),
            title='Author: {names}'.format(names=names),
            body='Nothing here yet.'
        )


def write_page(path, filename, **kwargs):
    filename = os.path.join(path, filename)
    log.fields(filename=filename).info('writing')
    with open(filename, 'wb') as f:
        f.write(PAGE_TEMPLATE.format(**kwargs))
