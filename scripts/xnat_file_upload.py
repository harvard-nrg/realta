#!/usr/bin/env python3 -u

import os
import sys
import yaxil
import logging
import requests
from argparse import ArgumentParser

logger = logging.getLogger('uploader')
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser()
    parser.add_argument('--xnat', default='cbscentral')
    parser.add_argument('--project', required=True)
    parser.add_argument('--subject', required=True)
    parser.add_argument('--session', default='TestSession02')
    parser.add_argument('--folder', default='behavioral_task_data',
        help='Desired resource folder name')
    parser.add_argument('--name', 
        help='Desired Resource file name')
    parser.add_argument('--confirm', action='store_true')
    parser.add_argument('file')
    args = parser.parse_args()

    auth = yaxil.auth(args.xnat)
    baseurl = auth.url.rstrip('/')
    aid = yaxil.accession(auth, args.session, args.project)

    # create folder and get resource
    folder = getresource(auth, aid, args.folder)
    if not folder:
        logger.info(f'creating folder {args.folder}')
        putresource(auth, aid, args.folder, confirm=args.confirm)
        folder = getresource(auth, aid, args.folder)

    # upload file to resource folder
    if not args.name:
        args.name = os.path.basename(args.file)
    upload(auth, aid, folder, args.file, args.name, confirm=args.confirm)
    
def upload(auth, aid, resource, filename, name, confirm=False):
    baseurl = auth.url.rstrip('/')
    rid = resource['xnat_abstractresource_id']
    url = f'{baseurl}/data/experiments/{aid}/resources/{rid}/files/{name}'
    params = {
        'file_upload': 'true'    
    }
    files = {
        'local_file': open(filename, 'rb')
    }
    logger.info(f'POST {url} with params {params} and file {filename}')
    if confirm:
        input('press enter to continue')
    resp = requests.post(
        url,
        params=params,
        files=files,
        cookies=auth.cookie,
    )
    if resp.status_code != requests.codes.ok:
        raise XnatError(f'POST {url} with params {params} returned {resp.status_code}')

def putresource(auth, aid, label, confirm=False):
    baseurl = auth.url.rstrip('/')
    url = f'{baseurl}/data/experiments/{aid}/resources/{label}'
    params = {
        'n': 1
    }
    logger.info(f'PUT {url} with params {params}')
    if confirm:
        input('press enter to continue')
    resp = requests.put(
        url,
        params=params,
        cookies=auth.cookie
    )
    if resp.status_code != requests.codes.ok:
        raise XnatError(f'PUT {url} with params {params} returned {resp.status_code}')

def getresource(auth, aid, label):
    baseurl = auth.url.rstrip('/')
    url = f'{baseurl}/data/experiments/{aid}/resources'
    params = {
        'all': 'true',
        'format': 'json'
    }
    resp = requests.get(
        url,
        params=params,
        cookies=auth.cookie
    )
    if resp.status_code != requests.codes.ok:
        raise XnatError(f'GET {url} with params {params} returned {resp.status_code}')
    for item in resp.json()['ResultSet']['Result']:
        if item['label'] == label:
            return item
    return None

class XnatError(Exception):
    pass

if __name__ == '__main__':
    main()
