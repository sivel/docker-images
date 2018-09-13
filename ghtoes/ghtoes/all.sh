#!/bin/sh

python -u github.py --all
jq .pull_requests github.json | python -u push_to_es.py --index ansible-pull-requests --type pr --server elasticsearch:9200
jq .issues github.json | python -u push_to_es.py --index ansible-issues --type issue --server elasticsearch:9200
