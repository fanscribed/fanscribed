import json
import os

from pyramid.response import Response
from pyramid.threadlocal import get_current_registry
from pyramid.view import view_config

from fanscribed.repos import commit_lock, repo_from_request


@view_config(
    request_method='GET',
    route_name='edit',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/edit.mako',
)
def edit(request):
    return dict(
        # ...
    )


@view_config(
    request_method='GET',
    route_name='view',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/view.mako',
)
def view(request):
    return dict(
        # ...
    )


@view_config(
    request_method='GET',
    route_name='speakers_txt',
    context='fanscribed:resources.Root',
)
def speakers_txt(request):
    repo = repo_from_request(request)
    master = repo.tree('master')
    blob = master['speakers.txt']
    return Response(body_file=blob.data_stream, content_type='text/plain')


@view_config(
    request_method='GET',
    route_name='transcription_json',
    context='fanscribed:resources.Root',
)
def transcription_json(request):
    repo = repo_from_request(request)
    master = repo.tree('master')
    blob = master['transcription.json']
    return Response(body_file=blob.data_stream, content_type='application/json')


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
        repo = repo_from_request(request)
        master = repo.tree('master')
        blob = master['transcription.json']
        transcription_info = json.load(blob.data_stream)
        if ('duration' not in transcription_info
            and 'bytes_total' not in transcription_info
            ):
            transcription_info['duration'] = int(duration)
            transcription_info['bytes_total'] = int(bytes_total)
            # Save transcription info.
            with commit_lock:
                repo.heads['master'].checkout()
                index = repo.index
                entry = index.entries[('transcription.json', 0)]
                filename = os.path.join(repo.working_dir, 'transcription.json')
                with open(filename, 'wb') as f:
                    json.dump(transcription_info, f, indent=4)
                index.add(['transcription.json'])
                os.environ['GIT_AUTHOR_NAME'] = identity_name
                os.environ['GIT_AUTHOR_EMAIL'] = identity_email
                index.commit('Initialize with duration and bytes_total')
            # Respond to client.
            response = 'Committed - Duration: {0}, Bytes: {1}'.format(duration, bytes_total)
        else:
            response = 'Already initialized'.format(duration, bytes_total)
    return Response(response, content_type='text/plain')
