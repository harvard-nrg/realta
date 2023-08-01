import os
import re
import sys
import json
import yaxil
import logging
import requests
from yaxil.exceptions import NoExperimentsError

logger = logging.getLogger()

class Tagger:
    def __init__(self, alias, filters, target, session, project=None, cache=None):
        self.auth = yaxil.auth(alias)
        self.filters = filters
        self.project = project
        self.cache = cache
        self.target = target 
        self.session = session
        self.updates = dict()

    def generate_updates(self):
        self.get_scan_listing()
        self.updates.update({
            'move_t1w_abcd': self.move_t1w_abcd(self.scans),
            'anat_t1w_abcd': self.anat_t1w_abcd(self.scans),
            'move_t2w_abcd': self.move_t2w_abcd(self.scans),
            'anat_t2w_abcd': self.anat_t2w_abcd(self.scans),
            'move_t1w_gsp': self.move_t1w_gsp(self.scans),
            'anat_t1w_gsp': self.anat_t1w_gsp(self.scans),
            'move_t2w_gsp': self.move_t2w_gsp(self.scans),
            'anat_t2w_gsp': self.anat_t2w_gsp(self.scans),
        })

    def apply_updates(self):
        self.upsert()

    def filter(self, modality):
        matches = []
        filt = self.filters[modality]
        for scan in self.scans:
            if scan['quality'] != 'usable':
                continue
            image_type = scan.get('image_type', None)
            if isinstance(image_type, str):
                scan['image_type'] = re.split('\\\+', scan['image_type'])
            for f in filt:
                match = True
                for key,value in iter(f.items()):
                    if key in scan and scan[key] != value:
                        match = False
                if match:
                    matches.append(scan)
        return matches

    def move_t1w_abcd(self, scans):
        updates = list()
        scans = self.filter('move_t1w_abcd')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'MOVE_T1w_ABCD_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def anat_t1w_abcd(self, scans):
        updates = list()
        scans = self.filter('anat_t1w_abcd')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'ANAT_T1w_ABCD_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def move_t2w_abcd(self, scans):
        updates = list()
        scans = self.filter('move_t2w_abcd')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'MOVE_T2w_ABCD_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def anat_t2w_abcd(self, scans):
        updates = list()
        scans = self.filter('anat_t2w_abcd')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'ANAT_T2w_ABCD_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def move_t1w_gsp(self, scans):
        updates = list()
        scans = self.filter('move_t1w_gsp')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'MOVE_T1w_GSP_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def anat_t1w_gsp(self, scans):
        updates = list()
        scans = self.filter('anat_t1w_gsp')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'ANAT_T1w_GSP_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def move_t2w_gsp(self, scans):
        updates = list()
        scans = self.filter('move_t2w_gsp')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'MOVE_T2w_GSP_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def anat_t2w_gsp(self, scans):
        updates = list()
        scans = self.filter('anat_t2w_gsp')
        for i,scan in enumerate(scans, start=1):
            sid = scan['id']
            session = scan['session_label']
            series = scan['series_description'].strip()
            note = scan['note'].strip()
            tag = f'ANAT_T2w_GSP_{i}'
            updates.append({
                'project': scan['session_project'],
                'subject': scan['subject_label'],
                'session': session, 
                'scan': sid,
                'series_description': series,
                'note': note,
                'tag': tag
            })
        return updates

    def upsert(self, confirm=False):
        updates = list(self._squeeze(self.updates))
        for scan in self.scans:
            sid = scan['id']
            note = scan['note']
            update = [x for x in updates if x['scan'] == sid]
            if not update:
                continue
            if len(update) > 1:
                raise UpsertError(f'found too many updates for scan {sid}')
            update = update.pop()
            note = update['note'].strip()
            tag = update['tag'].strip()
            if tag not in note:
                upsert = tag
                if note:
                    upsert = f'{tag} {note}'
                logger.info(f'setting note for scan {sid} to "{upsert}"')
                self.setnote(scan, text=upsert, confirm=False)
            else:
                logger.info(f"'{tag}' already in note '{note}'")


    def _squeeze(self, updates):
        for _,items in iter(updates.items()):
            for item in items:
                yield item

    def setnote(self, scan, text=None, confirm=False):
        if not text:
            text = ' '
        project = scan['session_project']
        subject = scan['subject_label'] 
        session = scan['session_label']
        scan_id = scan['id']
        baseurl = self.auth.url.rstrip('/')
        url = f'{baseurl}/data/projects/{project}/subjects/{subject}/experiments/{session}/scans/{scan_id}'
        params = {
            'xnat:mrscandata/note': text
        }
        logger.info(f'setting note for {session} scan {scan_id} to {text}')
        logger.info(f'PUT {url} params {params}')
        if confirm:
            input('press enter to execute request')
        r = requests.put(url, params=params, auth=(self.auth.username, self.auth.password))
        if r.status_code != requests.codes.OK:
            raise SetNoteError(f'response not ok for {url}')

    def get_scan_listing(self):
        '''
        Return scan listing as a list of dictionaries. 
        
        This function attempts to read the scan listing from a 
        cached JSON file. However, if a cached file doesn't exist, 
        one will be created by saving the output from yaxil.scans.
        '''
        cachefile = f'{self.session}.json'
        self.scans = None
        if not os.path.exists(cachefile):
            logger.info(f'cache miss {cachefile}')
            self.scans = list(yaxil.scans(self.auth, label=self.session))
            if self.cache:
                with open(cachefile, 'w') as fo:
                    fo.write(json.dumps(self.scans, indent=2))
        else:
            logger.info(f'cache hit {cachefile}')
            with open(cachefile) as fo:
                self.scans = json.loads(fo.read())

class BadArgumentError(Exception):
    pass
