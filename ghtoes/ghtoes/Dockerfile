FROM alpine

MAINTAINER Matt Martz matt@sivel.net

RUN apk add -U python jq ca-certificates openssl && update-ca-certificates;

RUN wget -q -O - https://bootstrap.pypa.io/get-pip.py | python;

RUN pip install -U requests elasticsearch;

RUN mkdir -p /usr/src/app && touch /usr/src/app/app.log;

ADD github.py /usr/src/app/github.py
ADD push_to_es.py /usr/src/app/push_to_es.py
#ADD issue_mapping.json /usr/src/app/issue_mapping.json
#ADD pr_mapping.json /usr/src/app/pr_mapping.json
ADD run.sh /usr/src/app/run.sh
ADD all.sh /usr/src/app/all.sh
ADD crontab /etc/crontabs/root

WORKDIR /usr/src/app

CMD crond -L /usr/src/app/cron.log && tail -f /usr/src/app/app.log
