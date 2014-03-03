{% set settings = pillar.app.settings %}
{% set user = pillar.app.user %}

{{ user }}:
  group:
    - present
  user:
    - present
    - gid_from_name: {{ user }}
    - groups:
      - {{ user }}
      - docker
      - sudo
    - shell: /bin/bash
    - require:
      - pkg: lxc-docker
      - group: {{ user }}

/home/{{ user }}/.bashrc:
  file.append:
    - text: |
        source /usr/local/bin/virtualenvwrapper.sh
        export WORKON_HOME=$HOME/.virtualenvs
        export PROJECT_HOME=$HOME/proj
        mkdir -p $PROJECT_HOME
