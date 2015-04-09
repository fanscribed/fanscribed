{% set db = pillar['app']['db'] %}

postgresql:
  pkg.installed: []
  service.running:
    - require:
      - pkg: postgresql

/etc/postgresql/9.3/main/postgresql.conf:
  file.append:
    - text: |
        listen_addresses = '*'
    - watch_in:
      - service: postgresql

/etc/postgresql/9.3/main/pg_hba.conf:
  file.append:
    - text: |
        host all all 0.0.0.0/0 md5
    - watch_in:
      - service: postgresql

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
    - encoding: UTF8
    - owner: {{ db['user'] }}
    - template: template0
    - require:
      - postgres_user: 'postgres user {{ db['user'] }}'
