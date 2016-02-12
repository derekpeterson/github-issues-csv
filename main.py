#/usr/bin/env python

import os
import csv
import requests


CLIENT_TOKEN = os.getenv('CLIENT_TOKEN')
API_DOMAIN = 'https://api.github.com'
ISSUES_PATH = '/repos/{0}/{1}/issues'


def process_issues(issues, user_mapping, outfile='issues.csv'):
    fieldnames = [
    'Summary',
    'Description',
    'Date Created',
    'Date Modified',
    'Reporter',
    'Assignee'
    ]

    with open(outfile, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for issue in issues:
            creator = issue.get('user', {}) or {}
            creator_name = creator.get('login')
            assignee = issue.get('assignee', {}) or {}
            assignee_name = assignee.get('login')

            if not issue.get('pull_request'):
                writer.writerow({
                'Summary': issue['title'],
                'Description': issue['body'],
                'Date Created': issue['created_at'],
                'Date Modified': issue['updated_at'],
                'Reporter': user_mapping.get(creator_name, creator_name),
                'Assignee': user_mapping.get(assignee_name, assignee_name),
                })

def get_issues(owner, repo):
    res = requests.get(API_DOMAIN + ISSUES_PATH.format(owner, repo),
                       params={ 'access_token':  CLIENT_TOKEN })
    return res.json()

def main(org, repo, outfile, user_mapping):
    issues = get_issues(org, repo)
    return process_issues(issues, outfile, user_mapping)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert GitHub issues to CSV')
    parser.add_argument('owner', help='The owner of the repo')
    parser.add_argument('repo', help='The repo to pull issues from')
    parser.add_argument('-o', '--outfile', help='The file to write the CSV to',
                        default='issues.csv')
    parser.add_argument('-u', '--user_mapping',
                        help='The mapping from GitHub users to user names')
    args = parser.parse_args()

    user_mapping = dict()
    if args.user_mapping:
        import json
        with open(args.user_mapping, 'r') as mapping_file:
            user_mapping = json.load(mapping_file)

    main(args.owner, args.repo, user_mapping, args.outfile)
