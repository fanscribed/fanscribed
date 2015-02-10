==========================
Fanscribed Developer Setup
==========================

.. image:: https://badges.gitter.im/Join%20Chat.svg
   :alt: Join the chat at https://gitter.im/fanscribed/fanscribed
   :target: https://gitter.im/fanscribed/fanscribed?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


Helpful shell aliases
=====================

``da`` -> ``django-admin.py``

``s`` -> ``da shell_plus``

``sup`` -> ``da supervisor``


One-time preparation
====================

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


Start the app and worker in foreground mode
===========================================

1.  Bring up the VM (if it's not up already)::

      $ vagrant up

2.  Connect to the VM via SSH::

      $ vagrant ssh

3.  Activate the ``app`` virtualenv and start services::

      $ workon app
      $ sup

4.  Visit `<http://localhost:8000/>`__.

    Or, if you have Zeroconf/Bonjour networking active,
    visit `<http://fanscribed-dev.local:8000/>`__.
    All Mac OSX systems support this.
    Many Ubuntu desktop systems do via `Avahi <http://en.wikipedia.org/wiki/Avahi_(software)>`__.


Updating the VM
===============

- When a requirements file changes, use Vagrant to reprovision::

    $ vagrant provision

- After a schema migration, resync the db::

    $ vagrant ssh
        # ... after connecting ...
    $ workon app
    $ da syncdb --migrate --noinput

