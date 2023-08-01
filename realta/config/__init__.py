import os
import yaml

__dir__ = os.path.dirname(__file__)

def tags():
    conf = os.path.join(
        __dir__,
        'tags.yaml'
    )
    return conf

def types():
    conf = os.path.join(
        __dir__,
        'types.csv'
    )
    return conf

