redis-server:
  pkg.installed: []
  service.running: []

# Listen on all interfaces
/etc/redis/redis.conf:
  file.comment:
    - regex: |
        ^bind 127.0.0.1
    - watch_in:
      - service: redis-server
