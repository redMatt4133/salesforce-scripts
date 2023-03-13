"""
    Package.xml template
    Pull latest API version from api_version.py
"""
from api_version import find_latest_version

API_VERSION = find_latest_version('https://my.salesforce.com/services/data/')

PKG_HEADER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Package xmlns="http://soap.sforce.com/2006/04/metadata">
'''

PKG_FOOTER = f'''\t<version>{API_VERSION}</version>
</Package>
'''
