#!/bin/bash
#
#   Configure sshd for PyCharm access,
#   then run sshd in the foreground.
#

echo root:docker | chpasswd

sed "s/without-password/yes/g" /etc/ssh/sshd_config > /etc/ssh/sshd_config2
sed "s/UsePAM yes/UsePAM no/g" /etc/ssh/sshd_config2 > /etc/ssh/sshd_config

mkdir /var/run/sshd

pip install -q fabric

/usr/sbin/sshd -D
