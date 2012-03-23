from pyramid.config import Configurator

import fanscribed.mp3
from fanscribed.resources import Root


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    # Override mp3splt location as needed.
    if 'fanscribed.mp3splt' in settings:
        fanscribed.mp3.MP3SPLT = settings['fanscribed.mp3splt']
        
    config = Configurator(root_factory=Root, settings=settings)

    # Routes
    config.add_route('robots_txt', '/robots.txt')

    config.add_route('read', '/')
    config.add_route('edit', '/edit')

    config.add_route('custom_css', '/custom.css')
    config.add_route('custom_js', '/custom.js')
    config.add_route('progress', '/progress')
    config.add_route('snippet_info', '/snippet_info')
    config.add_route('speakers_txt', '/speakers.txt')
    config.add_route('transcription_json', '/transcription.json')
    config.add_route('snippets_updated', '/snippets_updated')

    config.add_route('lock_snippet', '/lock_snippet')
    config.add_route('save_snippet', '/save_snippet')
    config.add_route('cancel_snippet', '/cancel_snippet')

    config.add_route('lock_review', '/lock_review')
    config.add_route('save_review', '/save_review')
    config.add_route('cancel_review', '/cancel_review')

    config.add_route('snippet_mp3', '/snippet.mp3')

    config.add_route('rss_basic', '/rss/basic')
    config.add_route('rss_completion', '/rss/completion')
    config.add_route('rss_kudos', '/rss/kudos')

    # Views.
    config.scan('fanscribed')
    config.add_static_view('static', 'fanscribed:static', cache_max_age=3600)

    return config.make_wsgi_app()
