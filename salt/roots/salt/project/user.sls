{% set user = pillar['project']['user'] %}

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
        source venv/bin/activate
