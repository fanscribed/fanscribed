from pyramid.config import Configurator
from fanscribed.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)
    # Routes: User-visible.
    config.add_route('view', '/')
    config.add_route('edit', '/edit')
    # Routes: Get data.
    config.add_route('speakers_txt', '/speakers.txt')
    config.add_route('transcription_json', '/transcription.json')
    # Routes: Save data.
    config.add_route('save_duration', '/save_duration')
    # Views.
    config.scan('fanscribed')
    config.add_static_view('static', 'fanscribed:static', cache_max_age=3600)
    return config.make_wsgi_app()
