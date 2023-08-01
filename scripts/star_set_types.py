#!/usr/bin/env python3 -u

import re
import sys
import csv
import json
import yaxil
import logging
import requests
import requests_cache
import realta.config as config
from argparse import ArgumentParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser(description='Set scan types')
    parser.add_argument('--xnat', default='cbscentral')
    parser.add_argument('--project')
    parser.add_argument('--session')
    parser.add_argument('--cache', action='store_true')
    parser.add_argument('--mapping', default=config.types())
    parser.add_argument('--do-updates', action='store_true')
    args = parser.parse_args()

    if args.cache:
        requests_cache.install_cache('cache', backend='sqlite')

    auth = yaxil.auth(args.xnat)
    
    # read in mapping file and unique it
    mapping = dict()
    with open(args.mapping) as fo:
        reader = csv.DictReader(fo)
        for row in reader:
            key = row['Series Description']
            value =  row['Type']
            if key in mapping and mapping[key] != value:
                raise Exception(f'found multiple instances of "{key}" with differing rename values')
            mapping[key] = value

    print('Project,Subject,Session,Scan,Series_Description,Type,Expected')
    for experiment in yaxil.experiments(auth, label=args.session, project=args.project):
        project = experiment.project
        subject = experiment.subject_label
        session = experiment.label
        for scan in yaxil.scans(auth, experiment=experiment):
            scanid = scan['ID']
            key = scan['series_description']
            actual = scan['type']
            expected = mapping[key]
            if key in mapping and actual != mapping[key]:
                print(f'{project},{subject},{session},{scanid},{key},{actual},{expected}')
                if args.do_updates:
                    settype(auth, experiment, scanid, expected)

def settype(auth, experiment, scanid, scan_type):
    baseurl = auth.url.rstrip('/')
    project = experiment.project
    subject = experiment.subject_label
    session = experiment.label
    url = f'{baseurl}/data/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scanid}'
    params = {
        'type': scan_type
    }
    logger.info(f'PUT {url} with {params}')
    r = requests.put(
        url,
        auth=(auth.username, auth.password),
        cookies=auth.cookie,
        params=params
    )
    if r.status_code != requests.codes.ok:
        raise SetTypeError(f'response status {r.status_code}')

class SetTypeError(Exception):
    pass

if __name__ == '__main__':
    main()
