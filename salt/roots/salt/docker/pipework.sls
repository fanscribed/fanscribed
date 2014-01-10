/usr/local/bin/pipework:
  file.managed:
    - source: salt://docker/pipework.sh
    - mode: 0755
