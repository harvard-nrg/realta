Réalta
======
A collection of data management scripts for the STAR study.

## Table of contents
1. [Installation](#installation)
2. [Set scan tags](#set-scan-tags)
3. [Audit existing tags](#audit-existing-tags)
   1. [cache requests](#cache-requests)
4. [Set scan types](#set-scan-types)
5. [Manually set scan metadata fields](#manually-set-scan-metadata-fields)
   1. [set the scan type](#set-the-scan-type)
   2. [set the scan note](#set-the-scan-note)
   3. [set the scan quality](#set-the-scan-quality)
6. [Send or resend DICOM files](#send-or-resend-dicom-files)
   1. [send files](#send-files)
   2. [resend files](#resend-files)
7. [Upload task data](#upload-task-data)

## Installation
You can install `realta` using `pip`

```bash
pip install git+https://github.com/harvard-nrg/realta.git
```

However, it is recommended to install `realta` within a virtual environment 
which will give you full control over installed dependencies

```bash
python3 -m venv realta
source realta/bin/activate
(realta) pip install git+https://github.com/harvard-nrg/realta.git
```

## Set scan tags
`star_set_tags.py` will tag all scans for a given STAR session on XNAT

```bash
star_set_tags.py --session 230101_STAR_1234_01 --do-updates
```

To inspect the tags _before_ they are set, omit `--do-updates` and specify an 
output file

```bash
star_set_tags.py --session 230101_STAR_1234_01 -o tags.json
```

In this example, the specified output file `tags.json` will contain any tags 
that would have been set by the script.

## Audit existing tags
`star_tag_audit.py` will sweep over all sessions within STAR and check if the 
tags that are currently set appear to be correct

```bash
star_tag_audit.py
```

This will output a CSV file to standard output with the `Expected` tags and the 
`Actual` tags that were found. 

### cache requests
`star_tag_audit.py` issues a _ton_ of HTTP requests to XNAT and will take a 
while to finish. If you stop and restart this script, it will start over from 
the beginning. You can use caching to speed things up.

> **Warning**
> Make sure you protect the cache file generated when using the `--cache` 
> argument. This file will contain a lot of sensitve information.

Passing `--cache` will record previously executed HTTP requests and their 
responses to a small sqlite database within your current working directory 
named `cache.sqlite3`. The next time you run `star_tag_audit.py` with the 
`--cache` argument, the script will read previously recorded responses from 
that file rather than sending a request to the server and waiting for a 
response. This is far less time consuming and will give you a noticable 
performance boost.

## Set scan types
`star_set_types.py` will set the scan types for a given STAR session on XNAT

```bash
star_set_types.py --session 230101_STAR_1234_01 --do-updates
```

Remove `--do-updates` to show the output from this script without actually 
changing anything in XNAT.

## Manually set scan metadata fields
`xnat_set.py` will allow you to arbitrarily set scan metadata fields from the 
command line. 

### set the scan `type`
To set the scan `type` for a given STAR session

```bash
xnat_set.py --session 230101_STAR_1234_01 --scan 1 --field type --value BOLD
```

### set the scan `note`
To set the scan `note` for a given STAR session

```bash
xnat_set.py --session 230101_STAR_1234_01 --scan 1 --field note --value "too much motion"
```

### set the scan `quality`
To set the scan `quality` (i.e., usability) for a given STAR session

> **Note**
> Scan `quality` can only be set to `usable`, `unusable`, or `questionable`.

```bash
xnat_set.py --session 230101_STAR_1234_01 --scan 1 --field quality --value unusable
```


## Send or resend DICOM files
`xnat_dicom_send.py` will allow you to send, or resend, your DICOM files to XNAT and 
have those files auto-archive into a given Project, Subject, and MR Session.

### send files
In the example below, `/path/to/dicom/files` should contain the DICOM files you
want to send to XNAT. 

> **Note** 
> In this example, the `PatientComments` header for each DICOM file will be 
> overwritten with the string 
>`Project:STAR_Study,Subject:STAR_1234,Session:230101_STAR_1234_01 AA:true`

```bash
xnat_dicom_send.py --project STAR_Study --subject STAR_1234 --session 230101_STAR_1234_01 /path/to/dicom/files
```

### resend files
If your DICOM files have already been uploaded to XNAT, but were archived under 
the wrong Project|Subject|Session, `xnat_dicom_send.py` can download those 
files and resend them under the correct Project|Subject|Session

> **Note**
> In this example, your DICOM files will be downloaded and saved into the 
> directory `/path/to/dicom/files`

```bash
xnat_dicom_send.py --project STAR_Study --subject STAR_1234 --session 230101_STAR_1234_01 --download-session 230101_STAR_1234_02 /path/to/dicom/files
```

## Upload task data
`xnat_file_upload.py` will allow you to upload behavioral task data to a folder 
named `behavioral_task_data` and assign the file a custom resource name

> **Note**
> In the following example, the local file `/path/to/task/data.csv` will be 
> uploaded to the folder `behavioral_task_data` and the XNAT file resource 
> will be assigned the name `Task_run1`

```bash
xnat_file_upload.py --project STAR_Study --subject STAR_1234 --session 230101_STAR_1234_01 --name Task_run1 /path/to/task/data.csv
```

If you omit `--name`, the XNAT resource will be assigned a name that is 
identical to the uploaded local file.
