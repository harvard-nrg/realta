#!/usr/bin/env python3 -u

import sys
import yaxil
import logging
import requests
import requests_cache
from argparse import ArgumentParser

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser()
    parser.add_argument('--xnat', default='cbscentral')
    parser.add_argument('--project')
    parser.add_argument('--session', required=True)
    parser.add_argument('--scan', required=True)
    parser.add_argument('--cache', action='store_true')
    parser.add_argument('--field', choices=['note', 'type', 'quality'])
    parser.add_argument('--value', required=True)
    parser.add_argument('--do-updates', action='store_true')
    args = parser.parse_args()

    if args.cache:
        requests_cache.install_cache('cache', backend='sqlite')

    if args.field == 'quality':
        choices = ['usable', 'questionable', 'unusable']
        if args.value not in choices:
            logger.critical(f'when using --field quality, value must be one of {choices}')
            sys.exit(1)
 
    auth = yaxil.auth(args.xnat)
    baseurl = auth.url.rstrip('/')

    experiments = list(yaxil.experiments(auth, label=args.session, project=args.project))
    if len(experiments) > 1:
        raise TooManyExperimentsError(f'found too many experiments with label {args.session}, use --project')
    experiment = experiments.pop()

    project = experiment.project
    subject = experiment.subject_label
    session = experiment.label
    url = f'{baseurl}/data/projects/{project}/subjects/{subject}/experiments/{session}/scans/{args.scan}'
    params = {
        f'xnat:mrscandata/{args.field}': args.value
    }
    logger.info(f'PUT {url} with params {params}')
    if args.do_updates:
        resp = requests.put(
            url,
            params=params,
            cookies=auth.cookie,
            auth=(auth.username, auth.password)
        )
        if resp.status_code != requests.codes.ok:
            raise SetFieldError(f'response status {resp.status_code}')

class FieldSetError(Exception):
    pass

class TooManyExperimentsError(Exception):
    pass

if __name__ == '__main__':
    main()
