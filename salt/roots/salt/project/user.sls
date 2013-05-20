{% set user = pillar['project_user'] %}

{{ user }}:
  group:
    - present
  user:
    - present
    - gid_from_name: {{ user }}
    - shell: /bin/bash
    - require:
      - group: {{ user }}

/home/{{ user }}/.bashrc:
  file.append:
    - text: |
        source venv/bin/activate
