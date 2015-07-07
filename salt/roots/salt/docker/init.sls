include:
  - docker.pipework

"Docker apt repository":
  pkgrepo:
    - managed
    - name: deb https://get.docker.io/ubuntu docker main
    - dist: docker
    - file: /etc/apt/sources.list.d/docker.list
    - keyid: 36A1D7869245C8950F966E92D8576A8BA88D21E9
    - keyserver: hkp://p80.pool.sks-keyservers.net:80

lxc-docker:
  pkg:
    - installed
    - version: 1.7.0
    - require:
      - pkgrepo: "Docker apt repository"
