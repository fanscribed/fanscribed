#!/bin/bash
#
# Watch the host volume for file changes.
# When a change occurs on the host volume, sync it to the docker filesystem.
# The ember-cli server then picks up the change in the docker filesystem.
#
# Why do we do this?
#
# When running a docker build, the entire contents of the `frontend/` dir
# is transferred to a volume used for building the container.
# You do not want to transfer `node_modules/` as this takes FOREVER!
#
# However, `node_modules/` needs to be inside the `frontend/` dir
# for tools to work correctly.
#
# This all works to prevent automatic Ember building when host files change,
# so we have to introduce a polling `rsync` loop
# as an intermediary to make sure the docker filesystem is kept up to date.
#
# We tried using the `watchdog` Python package and its `watchmedo` tool,
# but it was not compatible with the particular way host volumes are mounted
# into containers using boot2docker.

(
  while true; do
    sleep 2
    if [ ! -f /tmp/pause.syncing ]; then
      rsync \
        --quiet \
        --archive \
        --delete \
        --exclude-from=/usr/src/app.host/.dockerignore \
        /usr/src/app.host/ /usr/src/app/
    fi
  done
) &

# Now run the given ember-cli command.
/usr/local/bin/ember "$@"
