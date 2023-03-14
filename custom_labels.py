"""
    Import ElementTree to parse the custom labels file
"""
import re
import xml.etree.ElementTree as ET

# register the namespace to search the XML
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}
#filepath = 'force-app\main\default\labels\CustomLabels.labels-meta.xml'

def parse_custom_labels(label_file, diffs):
    """
        Parse the custom labels file
        and find labels with changes.
        Requires the current working directory file to be
        the same as to_ref argument in the parent script.
    """
    label_diff = diffs[label_file]
    diff_lines = label_diff.split('\n')
    root = ET.parse(label_file).getroot()
    component_type = 'CustomLabel'
    members = []
    for line in diff_lines:
        # space needed after + to not get the file name line the starts with +++
        if line.startswith('+ '):
            # can't get anything useful with label tag
            if 'labels' in line:
                continue
            # add net new label
            elif 'fullName' in line:
                labelname = re.search(r'>(.*?)<', line, flags=0).group(1)
                members.append(labelname)
            # find corresponding full name label if another element changed
            # doesn't matter if there are duplicates in this list
            # creating the dictionary will remove duplicate entries
            else:
                elementname = re.search(r'<(.*?)>', line, flags=0).group(1)
                textinside = re.search(r'>(.*?)<', line, flags=0).group(1)
                parentelement = root.findall(f".//sforce:labels[sforce:{elementname}='{textinside}']", ns)
                if parentelement is not None:
                    try:
                        members.append((parentelement[0].find('sforce:fullName', ns)).text)
                    except IndexError:
                        pass
    # convert list to tuple
    members = tuple(members)
    return component_type, members
