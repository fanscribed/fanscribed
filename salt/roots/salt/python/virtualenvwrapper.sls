include:
  - python

python-setuptools:
  pkg.installed

install pip:
  cmd.run:
    - name: "easy_install pip"
    - unless: test -f /usr/local/bin/pip

virtualenv:
  pip.installed:
    - require:
      - cmd: install pip

virtualenvwrapper:
  pip.installed:
    - require:
      - cmd: install pip
