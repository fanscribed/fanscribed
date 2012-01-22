import json
import os

import git

from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config

from fanscribed import repos


def _snippet_ms():
    registry = get_current_registry()
    settings = registry.settings
    snippet_seconds = int(settings['fanscribed.snippet_seconds'])
    return snippet_seconds * 1000


@view_config(
    request_method='GET',
    route_name='edit',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/edit.mako',
)
def edit(request):
    repo = repos.repo_from_request(request)
    master = repo.tree('master')
    transcription_info = repos.transcription_info(master)
    return dict(
        speakers=repos.speakers_text(master),
        transcription_info=transcription_info,
        transcription_info_json=json.dumps(transcription_info),
    )


@view_config(
    request_method='GET',
    route_name='view',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/view.mako',
)
def view(request):
    repo = repos.repo_from_request(request)
    master = repo.tree('master')
    raw_snippets = []
    for obj in master:
        if isinstance(obj, git.Blob):
            name, ext = os.path.splitext(obj.name)
            if ext == '.txt':
                try:
                    starting_point = int(name)
                except ValueError:
                    pass
                else:
                    raw_snippets.append((starting_point, obj.data_stream.read()))
    # Tease apart lines into left and right sides, replacing abbreviations with full expansion.
    snippets = []
    speakers_map = repos.speakers_map(master)
    for starting_point, text in raw_snippets:
        lines = []
        for line in text.splitlines():
            if ';' in line:
                left, right = line.split(';', 1)
            elif ':' in line:
                left, right = line.split(':', 1)
            else:
                left = ''
                right = line
            left = left.strip().lower()
            right = right.strip()
            if left in speakers_map:
                # Replace abbreviation with full expansion.
                left = speakers_map[left]
            lines.append((left, right))
        snippets.append((starting_point, lines))
    transcription_info = repos.transcription_info(master)
    return dict(
        snippets=snippets,
        speakers=repos.speakers_text(master),
        transcription_info=transcription_info,
        transcription_info_json=json.dumps(transcription_info),
    )


@view_config(
    request_method='GET',
    route_name='speakers_txt',
    context='fanscribed:resources.Root',
)
def speakers_txt(request):
    repo = repos.repo_from_request(request)
    master = repo.tree('master')
    text = repos.speakers_text(master)
    return Response(text, content_type='text/plain')


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
    repo = repos.repo_from_request(request)
    with repos.commit_lock:
        repo.heads['master'].checkout()
        index = repo.index
        filename = os.path.join(repo.working_dir, 'speakers.txt')
        with open(filename, 'wb') as f:
            f.write(text)
        index.add(['speakers.txt'])
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('Via web: update list of speakers')
    # Reload from repo and serve it up.
    master = repo.tree('master')
    text = repos.speakers_text(master)
    return Response(text, content_type='text/plain')


@view_config(
    request_method='GET',
    route_name='transcription_json',
    context='fanscribed:resources.Root',
)
def transcription_json(request):
    repo = repos.repo_from_request(request)
    master = repo.tree('master')
    info = repos.transcription_info()
    return Response(body=info, content_type='application/json')


@view_config(
    request_method='POST',
    route_name='save_duration',
    context='fanscribed:resources.Root',
)
def save_duration(request):
    registry = get_current_registry()
    settings = registry.settings
    init_password = settings['fanscribed.init_password'].strip()
    given_password = request.POST.getone('init_password').strip()
    if given_password != init_password:
        response = 'Wrong password'
    else:
        duration = int(request.POST.getone('duration'))
        bytes_total = int(request.POST.getone('bytes_total'))
        identity_name = request.POST.getone('identity_name')
        identity_email = request.POST.getone('identity_email')
        # Update transcription info.
        repo = repos.repo_from_request(request)
        master = repo.tree('master')
        blob = master['transcription.json']
        transcription_info = json.load(blob.data_stream)
        if ('duration' not in transcription_info
            and 'bytes_total' not in transcription_info
            ):
            transcription_info['duration'] = int(duration)
            transcription_info['bytes_total'] = int(bytes_total)
            # Save transcription info.
            with repos.commit_lock:
                repo.heads['master'].checkout()
                index = repo.index
                filename = os.path.join(repo.working_dir, 'transcription.json')
                with open(filename, 'wb') as f:
                    json.dump(transcription_info, f, indent=4)
                index.add(['transcription.json'])
                # Also save remaining snippets and reviews.
                locks = repos.get_locks(master)
                repos.save_locks(repo, index, locks)
                snippets = range(0, transcription_info['duration'], _snippet_ms())
                reviews = snippets[:-1]
                repos.save_remaining_snippets(repo, index, snippets)
                repos.save_remaining_reviews(repo, index, reviews)
                # Perform commit.
                os.environ['GIT_AUTHOR_NAME'] = identity_name
                os.environ['GIT_AUTHOR_EMAIL'] = identity_email
                index.commit('Via web: initialize based on duration of audio file')
            # Respond to client.
            response = 'Committed - Duration: {0}, Bytes: {1}'.format(duration, bytes_total)
        else:
            response = 'Already initialized'.format(duration, bytes_total)
    return Response(response, content_type='text/plain')


@view_config(
    request_method='POST',
    route_name='lock_snippet',
    context='fanscribed:resources.Root',
)
def lock_snippet(request):
    # unpack identity
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    with repos.commit_lock:
        repo = repos.repo_from_request(request)
        index = repo.index
        # find and lock available snippet
        starting_point, lock_secret_or_message = repos.lock_available_snippet(repo, index)
        # if found,
        if starting_point is not None:
            # commit with identity
            os.environ['GIT_AUTHOR_NAME'] = identity_name
            os.environ['GIT_AUTHOR_EMAIL'] = identity_email
            index.commit('Via web: lock snippet for editing')
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
    # unpack identity
    identity_name = request.POST.getone('identity_name')
    identity_email = request.POST.getone('identity_email')
    with repos.commit_lock:
        repo = repos.repo_from_request(request)
        index = repo.index
        # find and lock available review
        starting_point, lock_secret_or_message = repos.lock_available_review(repo, index)
        # if found,
        if starting_point is not None:
            # commit with identity
            os.environ['GIT_AUTHOR_NAME'] = identity_name
            os.environ['GIT_AUTHOR_EMAIL'] = identity_email
            index.commit('Via web: lock review for editing')
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
    snippet_text = request.POST.getone('snippet_text')
    with repos.commit_lock:
        # find and validate the lock
        repo = repos.repo_from_request(request)
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'snippet', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # save the snippet text
        repos.save_snippet_text(repo, index, starting_point, snippet_text)
        # remove the lock
        repos.remove_lock(repo, index, 'snippet', starting_point)
        # remove the snippet from remaining snippets
        repos.remove_snippet_from_remaining(repo, index, starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('Via web: save snippet')
    # return empty indicating success
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
        repo = repos.repo_from_request(request)
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
        index.commit('Via web: save review')
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
        repo = repos.repo_from_request(request)
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'snippet', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # remove the lock
        repos.remove_lock(repo, index, 'snippet', starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('Via web: cancel snippet')
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
        repo = repos.repo_from_request(request)
        index = repo.index
        if not repos.lock_is_valid(repo, index, 'review', starting_point, lock_secret):
            raise ValueError('Invalid lock')
        # remove the lock
        repos.remove_lock(repo, index, 'review', starting_point)
        # commit with identity
        os.environ['GIT_AUTHOR_NAME'] = identity_name
        os.environ['GIT_AUTHOR_EMAIL'] = identity_email
        index.commit('Via web: cancel review')
    # return empty indicating success
    return Response('', content_type='text/plain')
