from pyramid.response import Response
from pyramid.view import view_config

from fanscribed.repos import repo_from_request


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
