===================
 Fanscribed README
===================

Fanscribed helps people transcribe their favorite podcasts into text, by
fanning out the work involved to fans of the podcast, and making the
transcription process fun and interesting!

Below are some preliminary install notes.  If something doesn't work
for you, please open an issue for it:
`<https://github.com/fanscribed/fanscribed/issues/>`__.


Developer Prerequisites
=======================

- Linux, MacOSX, BSD, or similar POSIX environment.

- Latest Python 2.7

- Latest git

- Install virtualenv.  Recommended: also install virtualenvwrapper.


Initial environment setup
=========================

Using virtualenv, change to your favorite project directory, create
a new isolated environment, and activate it::

    $ virtualenv -p python2.7 fanscribed
    $ cd fanscribed
    $ source bin/activate

Or, using virtualenvwrapper::

    $ mkvirtualenv -p python2.7 fanscribed
    $ workon fanscribed
    $ cdvirtualenv

Clone the Fanscribed repository, install prerequisites, then install
Fanscribed in develop mode::

    $ git clone git@github.com:fanscribed/fanscribed
    $ cd fanscribed
    $ pip install .
    $ python setup.py develop

Create a sibling directory to hold transcript repositories used during
development::

    $ cd ..
    $ mkdir repos

Optional, but recommended: clone an existing transcript repository to
use as a testbed (instructions for creating new transcript repositories
forthcoming)::

    $ git clone git@github.com:readnoagenda/376 localhost:5000

The name "localhost" is used for your local clone, because Fanscribed
selects the repository to use based on the hostname you're connecting to
with your web browser.

Move back to your Fanscribed working copy, and create an INI file used
to run the web service::

    $ cd ../fanscribed
    $ cp development-local.ini.example development-local.ini


Starting the web server
=======================

Start the Fanscribed web server in development mode::

    $ paster serve --reload development-local.ini

If you are using the system Python on OSX, you may get a version mismatch
error about "zope.interface".  Upgrade the package in your isolated
environment to correct that problem::

    $ pip install -U zope.interface

Browse to `<http://localhost:5000/>`__, and you should now see a rendered
copy of the transcript you cloned above.


Load MP3 faster, and save bandwidth
===================================

If you browse to the "Edit" page, or begin playback on the "View" page,
you'll notice that the audio associated with the transcript loads from
an external website.

Follow these steps in a separate terminal session to serve the MP3 from
your development server:

- Go into your local working copy (repository) for the transcript.

- Type ``cat transcription.json`` to view metadata about the transcript.

- Copy the value for "audio_url" to the clipboard.

- Go into the "fanscribed/static" directory in your Fanscribed working
  copy.

- Run ``wget [paste URL here]`` to download the MP3 file.

- Go back into the transcript's working copy.

- Edit the "transcription.json" and change the "audio_url" value from
  "http://[remote_server_here]/[filename].mp3" to
  "http://localhost:5000/static/[filename].mp3".

- Commit the change::

    $ git commit -am "Use a local copy of audio"

- Reload the page in your browser, and begin streaming audio.  You should
  notice a considerable improvement in speed.
