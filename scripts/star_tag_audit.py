#!/usr/bin/env python3 -u

import re
import sys
import csv
import json
import yaxil
import logging
import requests
import argparse
import requests_cache
from argparse import ArgumentParser

logger = logging.getLogger('retag')
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser(description='Check XNAT scan tags for mismatches or ambiguities.')
    parser.add_argument('--xnat', default='cbscentral')
    parser.add_argument('--project')
    parser.add_argument('--session')
    parser.add_argument('--hide', action='store_true', help='Suppress NO_MATCH_FOUND and OK messages')
    parser.add_argument('--cache', action='store_true')
    args = parser.parse_args()

    if args.cache:
        requests_cache.install_cache('cache', backend='sqlite')

    auth = yaxil.auth(args.xnat)

    print('Project,Subject,Session,Tag,Expected,Actual,Status')
    for experiment in yaxil.experiments(auth, label=args.session, project=args.project):
        project = experiment.project
        subject = experiment.subject_label
        session = experiment.label
        result = gettags(auth, experiment)
        for tag,item in iter(result['tags'].items()):
            actual = item['actual']
            actual_str = ';'.join(actual)
            expected = item['expected']
            expected_str = ';'.join(expected)
            limit = item['limit']
            if not expected:
                if not args.hide:
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},NO_MATCH_FOUND')
            elif len(expected) > limit:
                if set(actual).issubset(set(expected)):
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},AMBIGUOUS(S)')
                else:
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},AMBIGUOUS')
            elif actual and expected != actual:
                if len(actual) <= limit and set(expected).issubset(set(actual)):
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},MISMATCH(S)')
                else:
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},MISMATCH')
            elif not set(expected).difference(set(actual)):
                if not args.hide:
                    print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},OK')
            else:
                print(f'{project},{subject},{session},{tag},{expected_str},{actual_str},SET_TAG')

def gettags(auth, experiment):
    result = {
        'tags': {
            'MOVE_T1w_ABCD': {
                'limit': 1,
                'actual': list(),
                'expected': list()
            },
            'ANAT_T1w_ABCD': {
                'limit': 1,
                'actual': list(),
                'expected': list()
            },
            'MOVE_T2w_ABCD': {
                'limit': 1,
                'actual': list(),
                'expected': list()
            },
            'ANAT_T2w_ABCD': {
                'limit': 1,
                'actual': list(),
                'expected': list()
            },
            'MOVE_T1w_GSP': {
                'limit': 2,
                'actual': list(),
                'expected': list()
            },
            'ANAT_T1w_GSP': {
                'limit': 2,
                'actual': list(),
                'expected': list()
            },
            'MOVE_T2w_GSP': {
                'limit': 2,
                'actual': list(),
                'expected': list()
            },
            'ANAT_T2w_GSP': {
                'limit': 2,
                'actual': list(),
                'expected': list()
            }
        }
    }
    for scan in yaxil.scans(auth, experiment=experiment):
        scanid = scan['ID']
        # expected
        if move_t1w_abcd_filter(scan):
            result['tags']['MOVE_T1w_ABCD']['expected'].append(scanid)
        if anat_t1w_abcd_filter(scan):
            result['tags']['ANAT_T1w_ABCD']['expected'].append(scanid)
        if move_t2w_abcd_filter(scan):
            result['tags']['MOVE_T2w_ABCD']['expected'].append(scanid)
        if anat_t2w_abcd_filter(scan):
            result['tags']['ANAT_T2w_ABCD']['expected'].append(scanid)
        if move_t1w_gsp_filter(scan):
            result['tags']['MOVE_T1w_GSP']['expected'].append(scanid)
        if anat_t1w_gsp_filter(scan):
            result['tags']['ANAT_T1w_GSP']['expected'].append(scanid)
        if move_t2w_gsp_filter(scan):
            result['tags']['MOVE_T2w_GSP']['expected'].append(scanid)
        if anat_t2w_gsp_filter(scan):
            result['tags']['ANAT_T2w_GSP']['expected'].append(scanid)
        # actual
        if move_t1w_abcd_note_filter(scan):
            result['tags']['MOVE_T1w_ABCD']['actual'].append(scanid)
        if anat_t1w_abcd_note_filter(scan):
            result['tags']['ANAT_T1w_ABCD']['actual'].append(scanid)
        if move_t2w_abcd_note_filter(scan):
            result['tags']['MOVE_T2w_ABCD']['actual'].append(scanid)
        if anat_t2w_abcd_note_filter(scan):
            result['tags']['ANAT_T2w_ABCD']['actual'].append(scanid)
        if move_t1w_gsp_note_filter(scan):
            result['tags']['MOVE_T1w_GSP']['actual'].append(scanid)
        if anat_t1w_gsp_note_filter(scan):
            result['tags']['ANAT_T1w_GSP']['actual'].append(scanid)
        if move_t2w_gsp_note_filter(scan):
            result['tags']['MOVE_T2w_GSP']['actual'].append(scanid)
        if anat_t2w_gsp_note_filter(scan):
            result['tags']['ANAT_T2w_GSP']['actual'].append(scanid)
    return result

def move_t1w_abcd_note_filter(scan):
    note = scan['note']
    return re.match('.*MOVE_T1w_ABCD_\d.*', note)

def anat_t1w_abcd_note_filter(scan):    
    note = scan['note']
    return re.match('.*ANAT_T1w_ABCD_\d.*', note)

def move_t2w_abcd_note_filter(scan):
    note = scan['note']
    return re.match('.*MOVE_T2w_ABCD_\d.*', note)

def anat_t2w_abcd_note_filter(scan):
    note = scan['note']
    return re.match('.*ANAT_T2w_ABCD_\d.*', note)

def move_t1w_gsp_note_filter(scan):
    note = scan['note']
    return re.match('.*MOVE_T1w_GSP_\d.*', note)

def anat_t1w_gsp_note_filter(scan):    
    note = scan['note']
    return re.match('.*ANAT_T1w_GSP_\d.*', note)

def move_t2w_gsp_note_filter(scan):
    note = scan['note']
    return re.match('.*MOVE_T2w_GSP_\d.*', note)

def anat_t2w_gsp_note_filter(scan):
    note = scan['note']
    return re.match('.*ANAT_T2w_GSP_\d.*', note)

def move_t1w_abcd_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T1w_setter' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'MOSAIC'] and
        quality == 'usable'
    )

def anat_t1w_abcd_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'ABCD_T1w_MPR_vNav' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'NORM'] and
        quality == 'usable'
    )

def move_t2w_abcd_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T2w_setter' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'MOSAIC'] and
        quality == 'usable'
    )

def anat_t2w_abcd_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'ABCD_T2w_SPC_vNav' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'NORM'] and
        quality == 'usable'
    )

def move_t1w_gsp_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T1_vNav_setter' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'MOSAIC'] and
        quality == 'usable'
    )

def anat_t1w_gsp_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T1_MEMPRAGE_GSP_vNavTrk RMS' and
        image_type == ['ORIGINAL', 'PRIMARY', 'OTHER', 'ND', 'NORM', 'MEAN'] and
        quality == 'usable'
    )

def move_t2w_gsp_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T2_vNav_setter' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'MOSAIC'] and
        quality == 'usable'
    )

def anat_t2w_gsp_filter(scan):
    scanid = scan['id']
    desc = scan['series_description']
    quality = scan['quality']
    image_type = scan.get('image_type', '')
    image_type = re.split('\\\+', image_type)
    return (
        desc == 'T2_SPACE_GSP_vNavTrk' and
        image_type == ['ORIGINAL', 'PRIMARY', 'M', 'ND', 'NORM'] and
        quality == 'usable'
    )

if __name__ == '__main__':
   main()
