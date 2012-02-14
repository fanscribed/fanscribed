# -*- coding: utf-8 -*-

import json
import os
import re
import unicodedata
import urlparse

import git

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config

from fanscribed import cache
from fanscribed.common import app_settings
from fanscribed import mp3
from fanscribed import repos


ROBOTS_TXT = """\
User-agent: *
Disallow: /edit
Disallow: /progress
Disallow: /speakers.txt
Disallow: /transcription.json
"""


def _progress_dicts(tree, transcription_info):
    if 'duration' in transcription_info:
        duration = transcription_info['duration']
        snippet_ms = _snippet_ms()
        snippets_total = duration / snippet_ms
        if duration % snippet_ms:
            snippets_total += 1
        snippets_remaining = len(repos.get_remaining_snippets(tree))
        snippets_completed = snippets_total - snippets_remaining
        snippets_percent = snippets_completed * 100 / snippets_total
        reviews_total = snippets_total - 1
        reviews_remaining = len(repos.get_remaining_reviews(tree))
        reviews_completed = reviews_total - reviews_remaining
        reviews_percent = reviews_completed * 100 / reviews_total
    else:
        snippets_total = 0
        snippets_remaining = 0
        snippets_completed = 0
        snippets_percent = 0
        reviews_total = 0
        reviews_remaining = 0
        reviews_completed = 0
        reviews_percent = 0
    return dict(
        snippets_progress=dict(
            total=snippets_total,
            completed=snippets_completed,
            percent=snippets_percent,
        ),
        reviews_progress=dict(
            total=reviews_total,
            completed=reviews_completed,
            percent=reviews_percent,
        ),
        # Support for embedding in mediawiki
        mediawiki=dict(
            snippets_percent=snippets_percent,
            reviews_percent=reviews_percent,
        ),
    )


# https://github.com/zacharyvoase/slugify/blob/master/src/slugify.py
def _slugify(text):
    """
    Slugify a unicode string.

    Example:

        >>> slugify(u"Héllø Wörld")
        u"hello-world"
    """
    return re.sub(
        r'[-\s]+',
        '-',
        unicode(
            re.sub(
                r'[^\w\s-]',
                '',
                unicodedata
                    .normalize('NFKD', text)
                    .encode('ascii', 'ignore')
            )
            .strip()
            .lower()
        )
    )


def _snippet_ms():
    snippet_seconds = int(app_settings()['fanscribed.snippet_seconds'])
    return snippet_seconds * 1000


def _split_lines_and_expand_abbreviations(text, speakers_map):
    lines = []
    if not isinstance(text, unicode):
        text = text.decode('utf8')
    text = text.strip()
    if text:
        # Tease apart lines into speaker and spoken, replacing abbreviations with full expansion.
        for line in text.splitlines():
            speaker = u''
            if u';' in line:
                abbreviation, spoken = line.split(u';', 1)
            else:
                abbreviation = u''
                spoken = line
            spoken = spoken.strip()
            if not spoken:
                # Ignore blank lines
                continue
            abbreviation = _slugify(abbreviation)
            if abbreviation in speakers_map:
                # Find full expansion for speaker's abbreviation.
                speaker = speakers_map[abbreviation]
            else:
                # No expansion found.
                speaker = abbreviation
            lines.append((abbreviation, speaker, spoken))
    return lines


def _standard_response(repo, commit):
    tree = commit.tree
    transcription_info, _ = repos.transcription_info(repo, commit)
    return dict(
        _progress_dicts(tree, transcription_info),
        latest_revision=repos.latest_revision(repo),
        custom_css_revision=repos.custom_css_revision(repo),
        custom_js_revision=repos.custom_js_revision(repo),
        speakers=repos.speakers_text(repo, commit)[0],
        transcription_info=transcription_info,
        transcription_info_json=json.dumps(transcription_info),
    )


@view_config(
    request_method='GET',
    route_name='robots_txt',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='robots_txt',
    context='fanscribed:resources.Root',
)
def robots_txt(request):
    return Response(ROBOTS_TXT, content_type='text/plain')


@view_config(
    request_method='GET',
    route_name='edit',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/edit.mako',
)
@view_config(
    request_method='HEAD',
    route_name='edit',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/edit.mako',
)
def edit(request):
    repo, commit = repos.repo_from_request(request, rev='master')
    return dict(
        _standard_response(repo, commit),
    )


@view_config(
    request_method='GET',
    route_name='read',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='read',
    context='fanscribed:resources.Root',
)
def read(request):
    repo, commit = repos.repo_from_request(request)
    # Return cached if found.
    cache_key = 'view-{0}'.format(commit.hexsha)
    content, mtime = cache.get_cached_content(cache_key)
    if content is None:
        mtime = commit.authored_date
        tree = commit.tree
        transcription_info, _ = repos.transcription_info(repo, commit)
        raw_snippets = {}
        for obj in tree:
            if isinstance(obj, git.Blob):
                name, ext = os.path.splitext(obj.name)
                if ext == '.txt':
                    try:
                        starting_point = int(name)
                    except ValueError:
                        pass
                    else:
                        raw_snippets[starting_point] = obj.data_stream.read().decode('utf8')
        # Go through all snippets, whether they've been transcribed or not.
        snippets = []
        speakers_map = repos.speakers_map(repo, commit)
        for starting_point in range(0, transcription_info['duration'], _snippet_ms()):
            text = raw_snippets.get(starting_point, '').strip()
            lines = _split_lines_and_expand_abbreviations(text, speakers_map)
            snippets.append((starting_point, lines))
        data = dict(
            _standard_response(repo, commit),
            snippets=sorted(snippets),
        )
        content = render('fanscribed:templates/view.mako', data, request=request)
        cache.cache_content(cache_key, content, mtime)
    return Response(content, date=mtime)


@view_config(
    request_method='GET',
    route_name='custom_css',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='custom_css',
    context='fanscribed:resources.Root',
)
def custom_css(request):
    # No rendering or processing, no need to cache.
    repo, commit = repos.repo_from_request(request)
    tree = commit.tree
    if 'custom.css' in tree:
        mtime = repo.iter_commits(commit, 'custom.css').next().authored_date
        blob = tree['custom.css']
        content = blob.data_stream.read().decode('utf8')
        return Response(content, date=mtime, content_type='text/css')
    else:
        # Not yet created.
        raise HTTPNotFound()


@view_config(
    request_method='GET',
    route_name='custom_js',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='custom_js',
    context='fanscribed:resources.Root',
)
def custom_js(request):
    # No rendering or processing, no need to cache.
    repo, commit = repos.repo_from_request(request)
    tree = commit.tree
    if 'custom.js' in tree:
        mtime = repo.iter_commits(commit, 'custom.js').next().authored_date
        blob = tree['custom.js']
        content = blob.data_stream.read().decode('utf8')
        return Response(content, date=mtime, content_type='text/javascript')
    else:
        # Not yet created.
        raise HTTPNotFound()


@view_config(
    request_method='GET',
    route_name='speakers_txt',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='speakers_txt',
    context='fanscribed:resources.Root',
)
def speakers_txt(request):
    # No rendering or processing, no need to cache.
    repo, commit = repos.repo_from_request(request)
    text, mtime = repos.speakers_text(repo, commit)
    return Response(text, content_type='text/plain', date=mtime)


@view_config(
    request_method='POST',
    route_name='speakers_txt',
    context='fanscribed:resources.Root',
)
def post_speakers_txt(request):
    text = request.POST.getone('text')
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    # Save transcription info.
    repo, commit = repos.repo_from_request(request, rev='master')
    with repos.commit_lock:
        repo.heads['master'].checkout()
        index = repo.index
        filename = os.path.join(repo.working_dir, 'speakers.txt')
        with open(filename, 'wb') as f:
            f.write(text.encode('utf8'))
        index.add(['speakers.txt'])
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('speakers: save')
    # Reload from repo and serve it up.
    text, mtime = repos.speakers_text(repo, commit)
    return Response(text, content_type='text/plain', date=mtime)


@view_config(
    request_method='GET',
    route_name='transcription_json',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='transcription_json',
    context='fanscribed:resources.Root',
)
def transcription_json(request):
    # No rendering or processing, no need to cache.
    repo, commit = repos.repo_from_request(request)
    info, mtime = repos.transcription_info(repo, commit)
    # Inject additional information into the info dict.
    settings = app_settings()
    info['snippet_ms'] = int(settings['fanscribed.snippet_seconds']) * 1000
    info['snippet_padding_ms'] = int(float(settings['fanscribed.snippet_padding_seconds']) * 1000)
    return Response(body=json.dumps(info), content_type='application/json')


@view_config(
    request_method='GET',
    route_name='progress',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='progress',
    context='fanscribed:resources.Root',
)
def progress(request):
    repo, commit = repos.repo_from_request(request)
    # Return cached if found.
    cache_key = 'progress-{0}'.format(commit.hexsha)
    content, mtime = cache.get_cached_content(cache_key)
    if content is None:
        tree = commit.tree
        info, _ = repos.transcription_info(repo, commit)
        content = json.dumps(_progress_dicts(tree, info))
        mtime = commit.authored_date
        cache.cache_content(cache_key, content, mtime=mtime)
    return Response(body=content, content_type='application/json', date=mtime)


@view_config(
    request_method='GET',
    route_name='snippet_info',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='snippet_info',
    context='fanscribed:resources.Root',
)
def snippet_info(request):
    repo, commit = repos.repo_from_request(request)
    starting_point = int(request.GET.getone('starting_point'))
    # Return cached if found.
    cache_key = 'snippet_info-{0}-{1}'.format(commit.hexsha, starting_point)
    content, mtime = cache.get_cached_content(cache_key)
    if content is None:
        starting_point = int(request.GET.getone('starting_point'))
        filename = '{0:016d}.txt'.format(starting_point)
        contributor_list = []
        mtime = None
        for commit in repo.iter_commits(commit, paths=filename):
            if mtime is None:
                # Use the most recent modification time.
                mtime = commit.authored_date
            contributor = dict(author_name=commit.author.name)
            if contributor not in contributor_list:
                contributor_list.append(contributor)
        contributor_list.reverse()
        info = dict(
            contributor_list=contributor_list,
        )
        content = json.dumps(info)
        cache.cache_content(cache_key, content, mtime=mtime)
    return Response(body=content, content_type='application/json', date=mtime)


def _banned_message(request):
    """Returns a reason why you're banned, or None if you're not banned."""
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).strip()
    ip_bans_filename = app_settings().get('fanscribed.ip_address_bans')
    email = request.POST.get('identity_email')
    if ip_bans_filename:
        with open(ip_bans_filename, 'rU') as f:
            for line in f.readlines():
                if ';' in line:
                    candidate_ip_address, reason = line.strip().split(';', 1)
                    if ip_address == candidate_ip_address:
                        return reason.strip()
    if email:
        email_bans_filename = app_settings().get('fanscribed.email_bans')
        if email_bans_filename:
            with open(email_bans_filename, 'rU') as f:
                for line in f.readlines():
                    if ';' in line:
                        candidate_email, reason = line.strip().split(';', 1)
                        if email == candidate_email:
                            return reason.strip()


@view_config(
    request_method='POST',
    route_name='lock_snippet',
    context='fanscribed:resources.Root',
)
def lock_snippet(request):
    # First make sure IP address is not banned.
    message = _banned_message(request)
    if message is not None:
        body = json.dumps({
            'lock_acquired': False,
            'message': message,
        })
        return Response(body, content_type='application_json')
    # unpack identity
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    # get snippet if specified
    desired_starting_point = request.POST.get('starting_point', None)
    if desired_starting_point is not None:
        desired_starting_point = int(desired_starting_point)
    with repos.commit_lock:
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        # find and lock available snippet
        starting_point, lock_secret_or_message = repos.lock_available_snippet(repo, index, desired_starting_point)
        # if found,
        if starting_point is not None:
            # commit with identity
            os.environ['GIT_AUTHOR_NAME'] = identity_name
            os.environ['GIT_AUTHOR_EMAIL'] = identity_email
            index.commit('snippet: lock')
            # return snippet info and text
            snippet_text = repos.snippet_text(repo, index, starting_point)
            body = json.dumps({
                'lock_acquired': True,
                'starting_point': starting_point,
                'ending_point': starting_point + _snippet_ms(),
                'lock_secret': lock_secret_or_message,
                'snippet_text': snippet_text,
            })
            return Response(body, content_type='application/json')
        else:
            # return message
            body = json.dumps({
                'lock_acquired': False,
                'message': lock_secret_or_message,
            })
            return Response(body, content_type='application/json')


@view_config(
    request_method='POST',
    route_name='lock_review',
    context='fanscribed:resources.Root',
)
def lock_review(request):
    # First make sure IP address is not banned.
    message = _banned_message(request)
    if message is not None:
        body = json.dumps({
            'lock_acquired': False,
            'message': message,
        })
        return Response(body, content_type='application_json')
    # unpack identity
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    with repos.commit_lock:
        # Ignore commit; we want to save to master.
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        # find and lock available review
        starting_point, lock_secret_or_message = repos.lock_available_review(repo, index)
        # if found,
        if starting_point is not None:
            # commit with identity
            os.environ['GIT_AUTHOR_NAME'] = identity_name
            os.environ['GIT_AUTHOR_EMAIL'] = identity_email
            index.commit('review: lock')
            # return review info and snippet texts
            review_text_1 = repos.snippet_text(repo, index, starting_point)
            review_text_2 = repos.snippet_text(repo, index, starting_point + _snippet_ms())
            body = json.dumps({
                'lock_acquired': True,
                'starting_point': starting_point,
                'ending_point': starting_point + (_snippet_ms() * 2),
                'lock_secret': lock_secret_or_message,
                'review_text_1': review_text_1,
                'review_text_2': review_text_2,
            })
            return Response(body, content_type='application/json')
        else:
            # return message
            body = json.dumps({
                'lock_acquired': False,
                'message': lock_secret_or_message,
            })
            return Response(body, content_type='application/json')


@view_config(
    request_method='POST',
    route_name='save_snippet',
    context='fanscribed:resources.Root',
)
def save_snippet(request):
    # unpack lock secret, starting point, identity, text
    lock_secret = request.POST.getone('lock_secret')
    starting_point = int(request.POST.getone('starting_point'))
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    snippet_text = request.POST.getone('snippet_text').strip()
    inline = request.POST.get('inline') == '1'
    with repos.commit_lock:
        # find and validate the lock
        # Ignore commit; we want to save to master.
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'snippet', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # save the snippet text
        repos.save_snippet_text(repo, index, starting_point, snippet_text)
        # remove the lock
        repos.remove_lock(repo, index, 'snippet', starting_point)
        # remove the snippet from remaining snippets
        if snippet_text:
            repos.remove_snippet_from_remaining(repo, index, starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        commit_message = 'snippet: save'
        if inline:
            commit_message += ' (inline)'
        index.commit(commit_message)
    return Response('', content_type='text/plain')


@view_config(
    request_method='POST',
    route_name='save_review',
    context='fanscribed:resources.Root',
)
def save_review(request):
    # unpack lock secret, starting point, identity, text
    lock_secret = request.POST.getone('lock_secret')
    starting_point = int(request.POST.getone('starting_point'))
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    review_text_1 = request.POST.getone('review_text_1')
    review_text_2 = request.POST.getone('review_text_2')
    with repos.commit_lock:
        # find and validate the lock
        # Ignore commit; we want to save to master.
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'review', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # save review texts
        repos.save_snippet_text(repo, index, starting_point, review_text_1)
        repos.save_snippet_text(repo, index, starting_point + _snippet_ms(), review_text_2)
        # remove the lock
        repos.remove_lock(repo, index, 'review', starting_point)
        # remove the review from remaining reviews
        repos.remove_review_from_remaining(repo, index, starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('review: save')
    # return empty indicating success
    return Response('', content_type='text/plain')


@view_config(
    request_method='POST',
    route_name='cancel_snippet',
    context='fanscribed:resources.Root',
)
def cancel_snippet(request):
    # unpack lock secret, starting point, identity
    lock_secret = request.POST.getone('lock_secret')
    starting_point = int(request.POST.getone('starting_point'))
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    with repos.commit_lock:
        # find and validate the lock
        # Ignore commit; we want to save to master.
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'snippet', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # remove the lock
        repos.remove_lock(repo, index, 'snippet', starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('snippet: cancel')
    # return empty indicating success
    return Response('', content_type='text/plain')


@view_config(
    request_method='POST',
    route_name='cancel_review',
    context='fanscribed:resources.Root',
)
def cancel_review(request):
    # unpack lock secret, starting point, identity
    lock_secret = request.POST.getone('lock_secret')
    starting_point = int(request.POST.getone('starting_point'))
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    with repos.commit_lock:
        # find and validate the lock
        # Ignore commit; we want to save to master.
        repo, commit = repos.repo_from_request(request, rev='master')
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'review', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # remove the lock
        repos.remove_lock(repo, index, 'review', starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('review: cancel')
    # return empty indicating success
    return Response('', content_type='text/plain')


@view_config(
    request_method='GET',
    route_name='snippet_mp3',
    context='fanscribed:resources.Root',
)
def snippet_mp3(request):
    repo, commit = repos.repo_from_request(request)
    # Get information needed from settings and repository.
    settings = app_settings()
    full_mp3 = os.path.join(
        settings['fanscribed.audio'],
        '{0}.mp3'.format(request.host),
    )
    transcription_info, _ = repos.transcription_info(repo, commit)
    duration = transcription_info['duration']
    snippet_cache = settings['fanscribed.snippet_cache']
    snippet_url_prefix = settings['fanscribed.snippet_url_prefix']
    # Get information needed from GET params.
    starting_point = int(request.GET.getone('starting_point'))
    length = int(request.GET.getone('length'))
    padding = int(request.GET.getone('padding'))
    snippet_path = mp3.snippet_path(
        full_mp3=full_mp3,
        duration=duration,
        output_path=snippet_cache,
        starting_point=starting_point,
        length=length,
        padding=padding,
    )
    relative_path = os.path.relpath(snippet_path, snippet_cache)
    snippet_url = urlparse.urljoin(snippet_url_prefix, relative_path)
    raise HTTPFound(location=snippet_url)


@view_config(
    request_method='GET',
    route_name='snippets_updated',
    context='fanscribed:resources.Root',
)
@view_config(
    request_method='HEAD',
    route_name='snippets_updated',
    context='fanscribed:resources.Root',
)
def snippets_updated(request):
    """Return formatted snippets that have been updated since the given revision."""
    repo, request_commit = repos.repo_from_request(request)
    since_rev = request.GET.getone('since')
    # Return cached if found.
    cache_key = 'updated-{0}-{1}'.format(request_commit.hexsha, since_rev)
    content, mtime = cache.get_cached_content(cache_key)
    if content is None:
        since_commit = repo.commit(since_rev)
        files_updated = set()
        for commit in repo.iter_commits(request_commit):
            # Have we reached the end?
            if commit == since_commit:
                break
            # Look for snippet changes.
            for filename in commit.stats.files:
                if len(filename) == 20 and filename.endswith('.txt'):
                    files_updated.add(filename)
        tree = request_commit.tree
        speakers_map = repos.speakers_map(repo, request_commit)
        snippets = []
        for filename in files_updated:
            starting_point = int(filename[:16])
            snippet = dict(
                starting_point=starting_point,
            )
            text = tree[filename].data_stream.read().strip()
            snippet['lines'] = _split_lines_and_expand_abbreviations(text, speakers_map)
            snippets.append(snippet)
        data = dict(
            latest_revision=repos.latest_revision(repo),
            snippets=snippets,
        )
        content = json.dumps(data)
        mtime = request_commit.authored_date
        cache.cache_content(cache_key, content, mtime)
    return Response(content, content_type='application/json', date=mtime)
