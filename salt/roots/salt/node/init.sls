install latest nodejs:
  cmd.script:
    - source: salt://node/nodesource-setup.sh

nodejs: pkg.installed
npm@~2.12.1: npm.installed
