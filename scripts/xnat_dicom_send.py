#!/usr/bin/env python3 -u

import os
import re
import sys
import yaxil
import pydicom
import logging
from argparse import ArgumentParser
from pydicom.errors import InvalidDicomError
from pynetdicom import AE, StoragePresentationContexts

logger = logging.getLogger('resend')
logging.basicConfig(level=logging.INFO)

def main():
    parser = ArgumentParser()
    parser.add_argument('--project', required=True)
    parser.add_argument('--subject', required=True)
    parser.add_argument('--session', required=True)
    parser.add_argument('--hostname', default='cbscentral.rc.fas.harvard.edu')
    parser.add_argument('--port', default=4444)
    parser.add_argument('--ae-title', default='CBSCENTRAL')
    parser.add_argument('--download-xnat', default='cbscentral')
    parser.add_argument('--download-project')
    parser.add_argument('--download-session')
    parser.add_argument('dir')
    args = parser.parse_args()
    
    if args.download_session:
        auth = yaxil.auth(args.download_xnat)
        logger.info(f'downloading {args.download_session} from {auth.url} to {args.dir}')
        yaxil.download(
            auth,
            label=args.download_session,
            project=args.download_project,
            scan_ids=['ALL'],
            out_dir=args.dir
        )

    ae = AE()
    ae.requested_contexts = StoragePresentationContexts
    assoc = ae.associate('cbscentral.rc.fas.harvard.edu', 4444, ae_title='CBSCENTRAL')

    study_instance_uid = None
    if assoc.is_established:
        for root,dirs,files in os.walk(args.dir):
            for f in files:
                fullfile = os.path.join(root, f)
                try:
                    ds = pydicom.read_file(fullfile)
                except InvalidDicomError as e:
                    logger.info(f'skipping non-dicom {fullfile}')
                    continue
                if not study_instance_uid:
                    study_instance_uid = ds.StudyInstanceUID
                if ds.StudyInstanceUID != study_instance_uid:
                    logger.warning(f'encountered DICOM files from multiple sessions')
                ds.PatientComments = f'Project:{args.project},Subject:{args.subject},Session:{args.session} AA:true'
                logger.info(f'sending {f}')
                status = assoc.send_c_store(ds)
                if status:
                    logger.info(f'C-STORE status: {status.Status}')
                else:
                    raise Exception('Connection timed out, was aborted or received invalid response')
    else:
        logger.error('Association rejected, aborted or never connected')

    assoc.release()

if __name__ == '__main__':
    main()
