include:
  - app.packages

{% set app = pillar.app %}
{% set virtualenv_path = app.virtualenv %}
{% set path = app.path %}
{% set user = app.user %}

{{ virtualenv_path }}:
  cmd.run:
    - name: "source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv app; cd {{ path }}; setvirtualenvproject"
    - user: {{ user }}
    - unless: "test -d {{ virtualenv_path }}"
    - require:
      - file: /home/{{ user }}/.bashrc
      - pip: virtualenvwrapper

{{ virtualenv_path }} pip packages:
  pip.installed:
    - requirements: {{ path }}/requirements/local.txt
    - user: {{ user }}
    - cwd: {{ path }}
    - bin_env: {{ virtualenv_path }}
    - no_chown: True
    - require:
      - cmd: {{ virtualenv_path }}
      - pkg: app packages
      - user: {{ user }}

{{ virtualenv_path }}/bin/python setup.py develop:
  cmd.run:
    - user: {{ user }}
    - cwd: {{ path }}
    - require:
      - cmd: {{ virtualenv_path }}
