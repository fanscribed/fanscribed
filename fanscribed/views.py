from pyramid.view import view_config


@view_config(
    route_name='edit',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/edit.pt',
)
def edit(request):
    return dict(
        # ...
    )


@view_config(
    route_name='view',
    context='fanscribed:resources.Root',
    renderer='fanscribed:templates/view.pt',
)
def view(request):
    return dict(
        # ...
    )
