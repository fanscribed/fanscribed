from pyramid.config import Configurator
from fanscribed.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    config.add_view('fanscribed.views.my_view',
                    context='fanscribed:resources.Root',
                    renderer='fanscribed:templates/mytemplate.pt')
    config.add_static_view('static', 'fanscribed:static', cache_max_age=3600)
    return config.make_wsgi_app()
