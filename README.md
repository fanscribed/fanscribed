# Fanscribed

## Developer quickstart

Install boot2docker.

Install fig.

Start services:

    $ fig up

In another terminal, sync database and create a superuser:

    $ ./figmanage syncdb --migrate --noinput
    $ ./figmanage createsuperuser

Browse to [localhost:8000](http://localhost:8000/) for the backend.

Browse to [localhost:4200](http://localhost:4200/) for the frontend.

## Using ember-cli via fig

Make sure you're in the top level of the repo.

    $ fig run frontend generate template transcripts
