#!/usr/bin/env python

import argparse
import json
import sys

from elasticsearch import Elasticsearch, RequestsHttpConnection
from elasticsearch.helpers import bulk


parser = argparse.ArgumentParser()
parser.add_argument('--index', default='index')
parser.add_argument('--type', default='type')
parser.add_argument('--mapping', type=argparse.FileType('r'))
parser.add_argument('file', type=argparse.FileType('r'), default=sys.stdin,
                    nargs='?')
parser.add_argument('--server', action='append')
parser.add_argument('--ssl', default=False, action='store_true')
args = parser.parse_args()

if not args.server:
    args.server = ['127.0.0.1:9200']

items = json.load(args.file)

if not isinstance(items, list):
    raise SystemExit(
        'file must contain a list of objects, not %r' % (
            items.__class__.__name__
        )
    )

es = Elasticsearch(args.server, verify_certs=True,
                   use_ssl=args.ssl,
                   connection_class=RequestsHttpConnection,
                   retry_on_timeout=True)

if not es.indices.exists(index=args.index):
    es.indices.create(index=args.index)

if args.mapping:
    mapping = es.indices.get_mapping(index=args.index)
    if args.type not in mapping[args.index]['mappings']:
        es.indices.put_mapping(
            doc_type=args.type,
            body=args.mapping.read(),
            index=args.index
        )


def chunker(items, length=250):
    i = 0
    while i * length < len(items):
        yield items[length * i:length * (i + 1)]
        i += 1


def actions(items):
    for chunk in chunker(items):
        yield [{
            '_op_type': 'update',
            '_index': args.index,
            '_type': args.type,
            '_id': item['number'],
            'doc': item,
            'doc_as_upsert': True,
        } for item in chunk]


for chunk in actions(items):
    try:
        print(bulk(es, chunk))
    except:
        print(bulk(es, chunk))
