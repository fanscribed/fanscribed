#!/bin/bash -ex

if [ "${VIRTUAL_ENV}" == "" ]; then
    echo "Must be in a virtualenv"
    exit 1
fi

cd $VIRTUAL_ENV
mkdir -p tmp-install-mp3splt
cd tmp-install-mp3splt

LIBDIR=${VIRTUAL_ENV}/lib
export LD_LIBRARY_PATH=${LIBDIR}
export LDFLAGS=-L${LIBDIR}
export PKG_CONFIG_PATH=${LIBDIR}/pkgconfig

(
    if ! [ -f libmad-0.15.1b.tar.gz ]; then
	wget http://sourceforge.net/projects/mad/files/libmad/0.15.1b/libmad-0.15.1b.tar.gz/download
    fi
    if ! [ -d libmad-0.15.1b ]; then
	tar xzvf libmad-0.15.1b.tar.gz
    fi
    cd libmad-0.15.1b
    ./configure --prefix=${VIRTUAL_ENV}
    make -j2
    make install
)

(
    if ! [ -f libogg-1.3.0.tar.gz ]; then
	wget http://downloads.xiph.org/releases/ogg/libogg-1.3.0.tar.gz
    fi
    if ! [ -d libogg-1.3.0 ]; then
	tar xzvf libogg-1.3.0.tar.gz
    fi
    cd libogg-1.3.0
    ./configure --prefix=${VIRTUAL_ENV}
    make -j2
    make install
)

(
    if ! [ -f libvorbis-1.3.2.tar.bz2 ]; then
	wget http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.2.tar.bz2
    fi
    if ! [ -d libvorbis-1.3.2 ]; then
	tar xjvf libvorbis-1.3.2.tar.gz
    fi
    cd libvorbis-1.3.2
    ./configure --prefix=${VIRTUAL_ENV}
    make -j2
    make install
)

(
    if ! [ -f libid3tag-0.15.1b.tar.gz ]; then
	wget http://sourceforge.net/projects/mad/files/libid3tag/0.15.1b/libid3tag-0.15.1b.tar.gz/download
    fi
    if ! [ -d libid3tag-0.15.1b ]; then
	tar xzvf libid3tag-0.15.1b.tar.gz
    fi
    cd libid3tag-0.15.1b
    ./configure --prefix=${VIRTUAL_ENV}
    make -j2
    make install
)

(
    if ! [ -f pcre-8.21.tar.bz2 ]; then
	wget http://sourceforge.net/projects/pcre/files/pcre/8.21/pcre-8.21.tar.bz2/download
    fi
    if ! [ -d pcre-8.21 ]; then
	tar xjvf pcre-8.21.tar.bz2
    fi
    cd pcre-8.21
    ./configure --prefix=${VIRTUAL_ENV}
    make -j2
    make install
)

(
    if ! [ -f libmp3splt-0.7.1.tar.gz ]; then
	wget http://prdownloads.sourceforge.net/mp3splt/libmp3splt-0.7.1.tar.gz
    fi
    if ! [ -d libmp3splt-0.7.1 ]; then
	tar xzvf libmp3splt-0.7.1.tar.gz
    fi
    cp patched-libmp3splt-0.7.1-plugins-mp3.h libmp3splt-0.7.1/plugins/mp3.h
    cd libmp3splt-0.7.1
    ./configure --prefix=${VIRTUAL_ENV} --with-mad=${VIRTUAL_ENV} --with-id3=${VIRTUAL_ENV} --with-ogg=${VIRTUAL_ENV} --with-vorbis=${VIRTUAL_ENV} --with-ltdl-lib=/usr/lib --with-ltdl-include=/usr/include
    make -j2
    make install
)

(
    if ! [ -f mp3splt-2.4.1.tar.gz ]; then
	wget http://prdownloads.sourceforge.net/mp3splt/mp3splt-2.4.1.tar.gz
    fi
    if ! [ -d mp3splt-2.4.1 ]; then
	tar xzvf mp3splt-2.4.1.tar.gz
    fi
    cd mp3splt-2.4.1
    ./configure --prefix=${VIRTUAL_ENV} --with-mp3splt=${VIRTUAL_ENV}
    make -j2
    make install
)

cat > ${VIRTUAL_ENV}/bin/vmp3splt <<EOF
#!/bin/bash
LD_LIBRARY_PATH=${VIRTUAL_ENV}/lib ${VIRTUAL_ENV}/bin/mp3splt $@
EOF
chmod +x ${VIRTUAL_ENV}/bin/vmp3splt
