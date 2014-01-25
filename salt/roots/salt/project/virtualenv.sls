include:
  - project.packages

{% set project = pillar.project %}
{% set virtualenv_path = project.virtualenv %}
{% set path = project.path %}
{% set user = project.user %}

{{ virtualenv_path }}:
  virtualenv.managed:
    - requirements: {{ path }}/requirements/local.txt
    - user: {{ user }}
    - cwd: {{ path }}
    - no_chown: True
    - require:
      - pkg: project packages
      - user: {{ user }}

{{ virtualenv_path }}/bin/python setup.py develop:
  cmd.run:
    - user: {{ user }}
    - cwd: {{ path }}
    - require:
      - virtualenv: {{ virtualenv_path }}
