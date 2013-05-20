include:
  - project.packages

{% set path = pillar['project_path'] %}
{% set user = pillar['project_user'] %}

{{ pillar['project_venv'] }}:
  virtualenv.managed:
    - requirements: {{ path }}/requirements/local.txt
    - runas: {{ user }}
    - cwd: {{ path }}
    - no_chown: True
    - require:
      - pkg: project packages
      - user: {{ user }}
