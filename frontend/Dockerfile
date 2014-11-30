FROM node

RUN npm install -g ember-cli bower

WORKDIR /usr/src/app

ADD package.json /usr/src/app/
RUN npm --verbose install

ADD bower.json /usr/src/app/
RUN bower --verbose --allow-root install

# TODO: Move this up to top.
RUN apt-get update
RUN apt-get -y install psmisc

ADD . /usr/src/app/

ENTRYPOINT ["/usr/local/bin/ember"]
CMD ["help"]
