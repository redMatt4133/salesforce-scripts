"""
    Import ElementTree to parse the custom labels file
"""
import xml.etree.ElementTree as ET

# register the namespace to search the XML
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
#filepath = 'force-app\main\default\labels\CustomLabels.labels-meta.xml'

def parse_custom_labels(label_file):
    """
        Parse the custom labels file
        and find all label names.
    """
    root = ET.parse(label_file).getroot()
    component_type = 'CustomLabel'
    members = []
    for labels in root.findall('sforce:labels', ns):
        members.append((labels.find('sforce:fullName', ns)).text)
    # convert list to tuple
    members = tuple(members)
    return component_type, members
