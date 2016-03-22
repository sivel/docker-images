FROM buildpack-deps:jessie

# remove several traces of debian python
RUN apt-get purge -y python.*

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# gpg: key 7D9DC8D2: public key "Martin v. Löwis <martin@v.loewis.de>" imported
ENV GPG_KEY 7D9DC8D2

ENV PYTHON_VERSION 2.4.5

# if this is called "PIP_VERSION", pip explodes with "ValueError: invalid truth value '<VERSION>'"
ENV PYTHON_PIP_VERSION 1.0

RUN set -ex \
	&& curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.bz2" -o python.tar.bz2 \
	&& curl -fSL "https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.bz2.asc" -o python.tar.bz2.asc \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$GPG_KEY" \
	&& gpg --batch --verify python.tar.bz2.asc python.tar.bz2 \
	&& rm -r "$GNUPGHOME" python.tar.bz2.asc \
	&& mkdir -p /usr/src/python \
	&& tar -xjC /usr/src/python --strip-components=1 -f python.tar.bz2 \
	&& rm python.tar.bz2 \
	\
	&& ln -s /usr/lib/x86_64-linux-gnu/* /usr/lib/ || true \
	&& ln -s /lib/x86_64-linux-gnu/* /lib/ || true \
	\
	&& cd /usr/src/python \
	&& ./configure --enable-shared --enable-unicode=ucs4 \
	&& make -j$(nproc) \
	&& make altbininstall \
	&& ldconfig \
	#&& make libinstall || true \
	&& make install \
	&& ldconfig \
	\
	&& curl -fSL "https://pypi.python.org/packages/source/s/setuptools/setuptools-0.6c9.tar.gz" -O \
	&& tar -xzf setuptools-0.6c9.tar.gz \
	&& cd setuptools-0.6c9 \
	&& python2.4 setup.py install \
	&& cd .. \
	\
	&& curl -fSL "https://pypi.python.org/packages/source/p/pip/pip-$PYTHON_PIP_VERSION.tar.gz" -O \
	&& tar -xzf pip-$PYTHON_PIP_VERSION.tar.gz \
	&& cd pip-$PYTHON_PIP_VERSION \
	&& python2.4 setup.py install \
	&& cd .. \
	\
	&& pip install --upgrade pip==$PYTHON_PIP_VERSION \
	&& find /usr/local \
		\( -type d -a -name test -o -name tests \) \
		-o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		-exec rm -rf '{}' + \
	&& rm -rf /usr/src/python

# install "virtualenv", since the vast majority of users of this image will want it
RUN pip install virtualenv==1.7.2

CMD ["python2.4"]
