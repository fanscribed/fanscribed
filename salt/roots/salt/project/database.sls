{% set db = pillar['project']['db'] %}

postgresql:
  pkg.installed

postgres user {{ db['user'] }}:
  postgres_user.present:
    - name: {{ db['user'] }}
    - createdb: True
    - password: {{ db['password'] }}
    - require:
      - pkg: postgresql

postgres database {{ db['name'] }}:
  postgres_database.present:
    - name: {{ db['name'] }}
    - encoding: utf8
    - owner: {{ db['user'] }}
    - template: template0
    - require:
      - postgres_user: {{ db['user'] }}
