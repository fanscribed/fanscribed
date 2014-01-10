include:
  - docker.pipework

"Docker apt repository":
  pkgrepo:
    - managed
    - name: deb http://get.docker.io/ubuntu docker main
    - dist: docker
    - file: /etc/apt/sources.list.d/docker.list
    - keyid: A88D21E9
    - keyserver: keyserver.ubuntu.com

lxc-docker:
  pkg:
    - latest
    - require:
      - pkgrepo: "Docker apt repository"
