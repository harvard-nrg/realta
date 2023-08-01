import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

requires = [
    'yaxil',
    'pydicom',
    'pynetdicom',
    'requests-cache'
]

about = dict()
with open(os.path.join(here, 'realta', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    packages=find_packages(),
    package_data={
        '': ['*.yaml', '*.csv']
    },
    include_package_data=True,
    scripts=[
        'scripts/xnat_set.py',
        'scripts/xnat_dicom_send.py',
        'scripts/xnat_file_upload.py',
        'scripts/star_set_types.py',
        'scripts/star_tag_audit.py',
        'scripts/star_set_tags.py'
    ],
    install_requires=requires
)
