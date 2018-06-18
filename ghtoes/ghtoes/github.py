#!/usr/bin/env python

import argparse
import json
import os
import time

import requests
from requests.exceptions import HTTPError, ConnectionError


RATE_LIMIT = '''
query {
  viewer {
    login
  }
  rateLimit {
    limit
    cost
    remaining
    resetAt
  }
}
'''


QUERY = '''
query {
  repository(owner:"ansible", name:"ansible") {
%s
%s
  }
}
'''

COMMON = '''
        assignees(first:100) {
          nodes {
            login
            name
          }
        }
        author {
          login
        }
        comments(last:100) {
          nodes {
            author {
              login
            }
            body
            bodyHTML
            bodyText
            createdAt
            createdViaEmail
            editor {
              login
            }
            lastEditedAt
            publishedAt
          }
        }
        labels(first:100) {
            nodes {
                name
            }
        }
        projectCards(first: 100) {
          nodes {
            column {
              name
              project {
                body
                name
                closed
              }
            }
          }
        }
        reactions(first:100) {
          nodes {
            content
            user {
              login
              name
            }
          }
        }
        body
        bodyHTML
        bodyText
        closed
        createdAt
        createdViaEmail
        editor {
          login
        }
        lastEditedAt
        locked
        milestone {
          number
          title
          state
          url
        }
        number
        publishedAt
        state
        title
        url
'''

ISSUES = '''
    issues(first:25, states:%(states)s%(cursor)s) {
      nodes {
%(common)s
      }
      pageInfo {
        endCursor
        hasNextPage
      }
      totalCount
    }
'''

PULL_REQUESTS = '''
    pullRequests(first:25, states:%(states)s%(cursor)s) {
      nodes {
%(common)s
        additions
        changedFiles
        deletions
        headRepository {
          name
          url
        }
        headRepositoryOwner {
          login
        }
        isCrossRepository
        mergeable
        merged
        mergedAt
        commits(first:100) {
          nodes {
            commit {
              author {
                date
                email
                name
                user {
                  login
                  name
                }
              }
              authoredByCommitter
              committer {
                date
                email
                name
                user {
                  login
                  name
                }
              }
              message
              messageBody
              status {
                state
              }
            }
          }
        }
        reviewRequests(first:100) {
          nodes {
            requestedReviewer {
              __typename
              ... on User {
                name
                login
              }
            }
          }
        }
        reviews(first:100) {
          nodes {
            author {
              login
            }
            bodyText
            state
          }
        }
      }
      pageInfo {
        endCursor
        hasNextPage
      }
      totalCount
    }
'''

def transform_nodes_of_things(item, key, subkey):
    item[key] = [n[subkey] for n in item[key]['nodes']]


def make_commenters(item):
    nodes = item['comments']['nodes']
    item['commenters'] = [
        n['author']['login'] for n in nodes if n['author']
    ]


def make_reviewers(item):
    nodes = item['reviews']['nodes']
    item['reviewers'] = [
        n['author']['login'] for n in nodes if n['author']
    ]


def transform_project_cards(item):
    nodes = item['projectCards']['nodes']

    project_cards = set()
    for n in nodes:
        if n['column'] and n['column']['project']:
            project_cards.add(
                '%s: %s' % (
                    n['column']['project']['name'],
                     n['column']['name']
                )
            )

    item['projectCards'] = list(project_cards)


def make_committers(item):
    nodes = item['commits']['nodes']

    committers = set()
    for node in nodes:
        if node['commit']['author']['user']:
            committers.add(node['commit']['author']['user']['login'])
        if node['commit']['committer']['user']:
            committers.add(node['commit']['committer']['user']['login'])

    item['committers'] = list(committers)


def transform(items):
    for item in items:
        transform_nodes_of_things(item, 'labels', 'name')
        transform_nodes_of_things(item, 'assignees', 'login')
        make_commenters(item)
        transform_nodes_of_things(item, 'reactions', 'content')
        transform_project_cards(item)
        try:
            make_committers(item)
        except KeyError:
            pass
        try:
            make_reviewers(item)
        except KeyError:
            pass


parser = argparse.ArgumentParser()
parser.add_argument('--all', action='store_true')
args = parser.parse_args()

output = {
    'pull_requests': [],
    'issues': [],
}

gql_s = requests.Session()
gql_s.headers = {
    'User-Agent': 'Awesome-Octocat-App',
    'Authorization': 'bearer %s' % os.getenv('GITHUB_TOKEN')
}

rest_s = requests.Session()
rest_s.headers = {
    'User-Agent': 'Awesome-Octocat-App',
    'Authorization': 'token %s' % os.getenv('GITHUB_TOKEN')
}

fetch = True
pull_requests = None
issues = None
loop = 1

if args.all:
    states = {
        'issues': '[OPEN, CLOSED]',
        'pull_requests': '[OPEN, CLOSED, MERGED]'
    }
else:
    states = {
        'issues': '[OPEN]',
        'pull_requests': '[OPEN]',
    }

while fetch:
    print('Loop: %d' % loop)
    filters = ['', '']
    if pull_requests:
        if pull_requests['pageInfo']['hasNextPage']:
            filters[0] = (
                PULL_REQUESTS % dict(
                    states=states['pull_requests'],
                    cursor=', after:"%s"' % (
                        pull_requests['pageInfo']['endCursor']
                    ),
                    common=COMMON
                )
            )
    else:
        filters[0] = PULL_REQUESTS % dict(
            states=states['pull_requests'],
            cursor='',
            common=COMMON
        )

    if issues:
        if issues['pageInfo']['hasNextPage']:
            filters[1] = (
                ISSUES % dict(
                    states=states['issues'],
                    cursor=', after:"%s"' % issues['pageInfo']['endCursor'],
                    common=COMMON
                )
            )
    else:
        filters[1] = ISSUES % dict(
            states=states['issues'],
            cursor='',
            common=COMMON
        )

    try:
        pr_had_next_page = (
            True if loop == 1 else pull_requests['pageInfo']['hasNextPage']
        )
    except Exception:
        pr_had_next_page = False
    try:
        issues_had_next_page = (
            True if loop == 1 else issues['pageInfo']['hasNextPage']
        )
    except Exception:
        issues_had_next_page = False

    print('PRs=%s Issues=%s' % (bool(filters[0]), bool(filters[1])))

    try:
        r = gql_s.post(
            'https://api.github.com/graphql',
            data=json.dumps({
                'query': QUERY % tuple(filters)
            })
        )
    except (HTTPError, ConnectionError) as e:
        print(str(e))
        continue

    resp = r.json()
    if 'errors' in resp:
        print('Error: %r' % (resp['errors'],))
        sleep_time = int(r.headers.get('Retry-After', 10))
        print('Sleeping %ds...' % sleep_time)
        time.sleep(sleep_time)
        continue

    if ((pr_had_next_page and
         'pullRequests' not in resp['data']['repository']) or
            (issues_had_next_page and
             'issues' not in resp['data']['repository'])):
        print('Error: %r' % (r.text,))
        sleep_time = int(r.headers.get('Retry-After', 10))
        print('Sleeping %ds...' % sleep_time)
        time.sleep(sleep_time)
        continue

    try:
        pull_requests = resp['data']['repository']['pullRequests']
    except KeyError:
        pull_requests = {
            'nodes': [],
            'pageInfo': {
                'hasNextPage': False
            }
        }

    try:
        issues = resp['data']['repository']['issues']
    except KeyError:
        issues = {
            'nodes': [],
            'pageInfo': {
                'hasNextPage': False
            }
        }

    if pull_requests:
        for node in pull_requests['nodes']:
            url = (
                'https://api.github.com/repos/ansible/ansible/pulls/%d/files' %
                (node['number'])
            )
            r = rest_s.get(url)
            node['files'] = {'nodes': r.json()}
        transform(pull_requests['nodes'])
        output['pull_requests'].extend(pull_requests['nodes'])

    if issues:
        transform(issues['nodes'])
        output['issues'].extend(issues['nodes'])

    fetch = (
        (pull_requests and pull_requests['pageInfo']['hasNextPage']) or
        (issues and issues['pageInfo']['hasNextPage'])
    )
    loop += 1

with open('github.json', 'w+') as f:
    json.dump(output, f, indent=4)


r = gql_s.post(
    'https://api.github.com/graphql',
    data=json.dumps({
        'query': RATE_LIMIT
    })
)

print(r.text)
