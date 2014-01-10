#!/bin/sh

mkdir -p /srv
if [ ! -f /srv/pillar ]; then
  ln -s /vagrant/fanscribed/salt/roots/pillar /srv/pillar
fi
if [ ! -f /srv/salt ]; then
  ln -s /vagrant/fanscribed/salt/roots/salt /srv/salt
fi
