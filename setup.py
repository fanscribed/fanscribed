import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(
    name='fanscribed',
    version='2.0',
    description='Fanscribed helps podcasts reach a wider audience using high-quality speech-to-text transcripts.',
    long_description=README + '\n\n' +  CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Django",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Elevencraft Inc.',
    author_email='matt@11craft.com',
    url='https://www.fanscribed.com/',
    license='MIT',
    keywords='web podcasts transcription',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points = """
        [console_scripts]
        fanscribed = fanscribed.manage:main
    """,
)
