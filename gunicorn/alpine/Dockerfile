FROM python:2-alpine

MAINTAINER Matt Martz matt@sivel.net

RUN mkdir -p /usr/src/app
ADD gunicorn.conf.py /usr/src/app/gunicorn.conf.py
WORKDIR /usr/src/app

ONBUILD ARG SRC=.
ONBUILD COPY ${SRC} /usr/src/app

ONBUILD RUN pip install --no-cache-dir -r requirements.txt
ONBUILD RUN pip install gunicorn

EXPOSE 8000
ENTRYPOINT ["gunicorn", "-c", "gunicorn.conf.py"]
