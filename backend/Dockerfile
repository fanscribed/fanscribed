FROM ubuntu:trusty

ENV PYTHONUNBUFFERED 1

# Faster mirrors
RUN sed -i -e 's/archive.ubuntu.com/mirrors.digitalocean.com/' /etc/apt/sources.list
RUN sed -i -e 's/security.ubuntu.com/mirrors.digitalocean.com/' /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y \
  build-essential \
  nodejs \
  npm \
  python2.7-dev \
  python-setuptools \
  ssh \
  libpq-dev \
  curl \
  libjpeg-dev \
  liblcms2-dev \
  libncurses5-dev \
  libxml2-dev \
  libxslt1-dev \
  mp3splt \
  libav-tools \
  libavcodec-extra-54
RUN easy_install pip

RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN npm install --global less

# rollup
RUN apt-get -y install git

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
ADD requirements.txt /usr/src/app/
ADD requirements/ /usr/src/app/requirements/

RUN pip install -r requirements.txt

# rollup
RUN pip install -r requirements/local.txt

ADD . /usr/src/app/

RUN python setup.py develop

CMD /bin/bash
