#!/bin/sh

python -u github.py --all
jq .pull_requests github.json | python -u push_to_es.py --index ansible-pull-requests --type pr --server elasticsearch:9200 --mapping pr_mapping.json
jq .issues github.json | python -u push_to_es.py --index ansible-issues --type issue --server elasticsearch:9200 --mapping issue_mapping.json
