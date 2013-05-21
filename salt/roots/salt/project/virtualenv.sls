include:
  - project.packages

{% set project = pillar['project'] %}
{% set path = project['path'] %}
{% set user = project['user'] %}

{{ project['virtualenv'] }}:
  virtualenv.managed:
    - requirements: {{ path }}/requirements/local.txt
    - runas: {{ user }}
    - cwd: {{ path }}
    - no_chown: True
    - require:
      - pkg: project packages
      - user: {{ user }}
