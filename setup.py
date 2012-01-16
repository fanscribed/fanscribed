import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'pyramid_debugtoolbar',
]

setup(
    name='fanscribed',
    version='1.0',
    description='fanscribed helps people transcribe their favorite podcasts into text',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Matthew Scott',
    author_email='matt@11craft.com',
    url='https://github.com/fanscribed/fanscribed/',
    license='BSD',
    keywords='web pyramid pylons podcasts transcription',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="fanscribed",
    entry_points = """
        [paste.app_factory]
        main = fanscribed:main
    """,
    paster_plugins=[
        'pyramid',
    ],
)
