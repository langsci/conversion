from pyramid.config import Configurator


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('result', '/result')
    config.add_route('doc2bib', '/doc2bib')
    config.add_route('normalizebib', '/normalizebib')
    config.add_route('doc2tex', '/doc2tex')
    config.add_route('sanitycheck', '/sanitycheck')
    config.add_route('overleafsanity', '/overleafsanity')
    config.scan()
    return config.make_wsgi_app()
