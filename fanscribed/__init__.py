from pyramid.config import Configurator

from fanscribed.resources import Root

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(root_factory=Root, settings=settings)

    # Routes
    config.add_route('view', '/')
    config.add_route('edit', '/edit')
    config.add_route('speakers_txt', '/speakers.txt')
    config.add_route('transcription_json', '/transcription.json')

    config.add_route('save_duration', '/save_duration')

    config.add_route('lock_snippet', '/lock_snippet')
    config.add_route('save_snippet', '/save_snippet')
    config.add_route('cancel_snippet', '/cancel_snippet')

    config.add_route('lock_review', '/lock_review')
    config.add_route('save_review', '/save_review')
    config.add_route('cancel_review', '/cancel_review')

    # Views.
    config.scan('fanscribed')
    config.add_static_view('static', 'fanscribed:static', cache_max_age=3600)

    return config.make_wsgi_app()
