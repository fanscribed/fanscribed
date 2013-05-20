include:
  - project.packages

{% set user = pillar['project_user'] %}

{{ pillar['project_venv'] }}:
  virtualenv.managed:
    - requirements: {{ pillar['project_path'] }}/requirements.txt
    - runas: {{ user }}
    - no_chown: True
    - require:
      - pkg: project packages
      - user: {{ user }}
