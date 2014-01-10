#!/bin/sh

sed -i -e 's/us.archive.ubuntu.com/mirrors.digitalocean.com/' /etc/apt/sources.list
sed -i -e 's/security.ubuntu.com/mirrors.digitalocean.com/' /etc/apt/sources.list

apt-get update
