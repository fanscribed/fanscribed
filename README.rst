==========================
Fanscribed Developer Setup
==========================

..  image:: https://travis-ci.org/fanscribed/fanscribed.svg?branch=master
    :target: https://travis-ci.org/fanscribed/fanscribed

..  image:: https://badges.gitter.im/Join%20Chat.svg
    :alt: Join the chat at https://gitter.im/fanscribed/fanscribed
    :target: https://gitter.im/fanscribed/fanscribed?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


Helpful shell aliases
=====================

``da`` -> ``django-admin.py``

``s`` -> ``da shell_plus``

``sup`` -> ``da supervisor``


Vagrant: One-time preparation
=============================

1.  Download and install `Vagrant <http://vagrantup.com/>`__.
    Review the basics of Vagrant if you haven't used it recently.

2.  Clone this repo and change to its directory::

      $ git clone git@github.com:fanscribed/fanscribed
      $ cd fanscribed

3.  Make a ``Vagrantfile``, then edit it
    to choose between Virtualbox or VMware::

      $ cp Vagrantfile.example Vagrantfile
      $ $EDITOR Vagrantfile

4.  Bring up the VM for the first time::

      $ vagrant up

    If you're using the `VMware provider for Vagrant <http://www.vagrantup.com/vmware>`__,
    pass the ``provider`` name appropriate to your environment::

      $ vagrant up --provider=vmware_fusion
      $ vagrant up --provider=vmware_workstation

    If you run into problems during provisioning::

      $ vagrant ssh
      $ sudo salt-call --local state.highstate

    If some states fail, run ``state.highstate`` again.

5.  Connect to the VM via SSH::

      $ vagrant ssh

6.  Activate the ``app`` virtualenv::

      $ workon app

7.  Synchronize the database::

      $ da syncdb --migrate --noinput
      $ da loaddata task_types
      $ da waffle_update waffle.yaml

8.  Create some demo data::

      $ da fix demo


Vagrant: Start the app and worker in foreground mode
====================================================

1.  Bring up the VM (if it's not up already)::

      $ vagrant up

2.  Connect to the VM via SSH::

      $ vagrant ssh

3.  Activate the ``app`` virtualenv and start services::

      $ workon app
      $ sup

4.  If you have Zeroconf/Bonjour networking active,
    visit `<http://fanscribed-dev.local:7777/>`__.

    All Mac OSX systems support this.
    Many Ubuntu desktop systems do via `Avahi <http://en.wikipedia.org/wiki/Avahi_(software)>`__.


OS X (optional): One-time preparation
=====================================

You can use the Vagrant VM as a data store, running PostgreSQL and Redis,
and run your development environment on your OS X host.

1.  Set up a virtualenv using mkvirtualenv.
    (That is outside the scope of this README)

2.  Activate the virtualenv; let's say you called it ``fs``::

      $ workon fs

3.  Install the development packages::

      $ pip install -r requirements/local.txt

4.  Update ``postactivate`` script::

      $ cdvirtualenv bin
      $ vim postactivate

    ...add this content to it::

      export DJANGO_SETTINGS_MODULE=fanscribed.settings.local
      export DATABASE_URL=postgres://fanscribed:fanscribed@fanscribed-dev.local:5432/fanscribed
      export BROKER_URL=redis://fanscribed-dev.local:6379/0
      export REDIS_CACHE_LOCATION=fanscribed-dev.local:6379:1
      export TEST_REDIS_CACHE_LOCATION=fanscribed-dev.local:6379:2
      alias da='django-admin.py'
      alias s='da shell_plus'
      alias sup='da supervisor'

    ...then go back to your ``fanscribed`` dir::

      $ cd -

Now you can run any of the standard commands as you would inside the VM::

    $ da fix demo
    $ sup


Updating the VM
===============

- When a requirements file changes, use Vagrant to reprovision::

    $ vagrant provision

- After a schema migration, resync the db::

    $ vagrant ssh
        # ... after connecting ...
    $ workon app
    $ da syncdb --migrate --noinput


Running tests
=============

With a virtualenv activated::

    $ python runtests.py

Arguments are passed along to ``django-admin.py test``::

    $ python runtests.py --failfast

You can skip slower tests using the ``FAST_TEST`` environment var::

    $ FAST_TEST=1 python runtests.py

