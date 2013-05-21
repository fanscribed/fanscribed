============================
 Fanscribed Developer Setup
============================


One-time preparation
====================

1.  Download and install `Vagrant <http://vagrantup.com/>`__.
    Review the basics of Vagrant if you haven't used it recently.

2.  Install the `vagrant-salt <http://www.vagrantup.com/vmware>`__ plugin::

      $ vagrant plugin install vagrant-salt

3.  Clone this repo and change to its directory::

      $ git clone https://github.com/fanscribed/fanscribed
      $ cd fanscribed

4.  Make a ``Vagrantfile``, then edit it
    to choose between Virtualbox or VMware::

      $ cp Vagrantfile.example Vagrantfile
      $ $EDITOR Vagrantfile

4.  Bring up the VM for the first time::

      $ vagrant up

    If you're using the `VMware provider for Vagrant <http://www.vagrantup.com/vmware>`__,
    pass the ``provider`` name appropriate to your environment::

      $ vagrant up --provider=vmware_fusion
      $ vagrant up --provider=vmware_workstation

5.  Connect to the VM via SSH::

      $ vagrant ssh

6.  Synchronize the database::

      $ fanscribed syncdb --migrate --noinput

7.  Create a superuser::

      $ fanscribed createsuperuser


Start the web server in foreground mode
=======================================

1.  Bring up the VM (if it's not up already)::

      $ vagrant up

2.  Connect to the VM via SSH::

      $ vagrant ssh

3.  Start the development web server::

      $ fanscribed runserver

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
    $ fanscribed syncdb --migrate --noinput

