#/usr/bin/env python

import os
import csv
import requests


CLIENT_TOKEN = os.getenv('CLIENT_TOKEN')
API_DOMAIN = 'https://api.github.com'
ISSUES_PATH = '/repos/{0}/{1}/issues'


def process_issues(issues, outfile='issues.csv'):
    fieldnames = [
    'Summary',
    'Description',
    'Date Created',
    'Date Modified'
    ]
    with open(outfile, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for issue in issues:
            if not issue.get('pull_request'):
                writer.writerow({
                'Summary': issue['title'],
                'Description': issue['body'],
                'Date Created': issue['created_at'],
                'Date Modified': issue['updated_at']
                })

def get_issues(owner, repo):
    res = requests.get(API_DOMAIN + ISSUES_PATH.format(owner, repo),
                       params={ 'access_token':  CLIENT_TOKEN })
    return res.json()

def main(org, repo, outfile):
    issues = get_issues(org, repo)
    return process_issues(issues, outfile)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert GitHub issues to CSV')
    parser.add_argument('owner', help='The owner of the repo')
    parser.add_argument('repo', help='The repo to pull issues from')
    parser.add_argument('-o', '--outfile', help='The file to write the CSV to',
                        default='issues.csv')
    args = parser.parse_args()

    main(args.owner, args.repo, args.outfile)
