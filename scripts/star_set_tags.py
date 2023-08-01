#!/usr/bin/env python3 -u

import os
import re
import sys
import json
import yaml
import yaxil
import string
import logging
import requests
import collections
import argparse as ap
from io import StringIO
from yaml.representer import Representer
from yaxil.exceptions import NoExperimentsError
from realta.tagger import Tagger
import realta.config as config 

logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.INFO)

yaml.add_representer(collections.defaultdict, Representer.represent_dict)

def main():
    parser = ap.ArgumentParser()
    parser.add_argument('--xnat', default='cbscentral',
        help='XNAT alias')
    parser.add_argument('--project',
        help='XNAT project')
    parser.add_argument('--session', required=True,
        help='Label of XNAT MR Session')
    parser.add_argument('-o', '--output-file',
        help='Output summary of updates')
    parser.add_argument('--filters', default=config.tags(),
        help='Filters configuration file') 
    parser.add_argument('--confirm', action='store_true',
        help='Prompt user to confirm every update')
    parser.add_argument('--do-updates', action='store_true',
        help='Execute updates')
    args = parser.parse_args()

    with open(args.filters) as fo:
        filters = yaml.load(fo, Loader=yaml.SafeLoader)

    tagger = Tagger(args.xnat, filters, ['all'], args.session)
    tagger.generate_updates()

    if args.output_file:
        with open(args.output_file, 'w') as fo:
            js = json.dumps(tagger.updates, indent=2)
            fo.write(js)
    if args.do_updates:
        tagger.apply_updates()

if __name__ == '__main__':
    main()

