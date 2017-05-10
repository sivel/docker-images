FROM ubuntu:trusty

MAINTAINER Matt Martz matt@sivel.net

RUN apt-get clean; apt-get update -y;
RUN apt-get install -y \
#    debianutils \
#    make \
#    gcc \
    python2.7 \
    python-dev \
    python-pip \
    ca-certificates
#    libevent-2.0-5 \
#    libevent-1.4-2 \
#    libevent-dev \
#    libldap2-dev \
#    libsasl2-dev \
#    libssl-dev \
#    freetds-dev \
#    libffi-dev
RUN pip install -U pip

RUN mkdir -p /usr/src/app
ADD gunicorn.conf.py /usr/src/app/gunicorn.conf.py
WORKDIR /usr/src/app

ONBUILD ARG SRC=.
ONBUILD COPY ${SRC} /usr/src/app

ONBUILD RUN pip install --no-cache-dir -r requirements.txt
ONBUILD RUN pip install gunicorn

EXPOSE 8000
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]
