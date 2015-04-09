install latest nodejs:
  cmd.script:
    - source: salt://node/nodesource-setup.sh

nodejs: pkg.installed
npm@~2.5.1: npm.installed
