"""
    Import ElementTree to parse the manual packae.xml
"""
import xml.etree.ElementTree as ET

# register_namespace only influences serialization, not search
# use both
METADATA_LINK = 'http://soap.sforce.com/2006/04/metadata'
ET.register_namespace('', METADATA_LINK)
ns = {'sforce': METADATA_LINK}


def parse_manual_package(package_path, changes):
    """
        Parse the manual package.xml and
        append the metadata types to the existing
        changes dictionary
    """
    root = ET.parse(package_path).getroot()

    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = (metadata_type.find('sforce:name', ns)).text
        # find all matches if there are multiple memebers for 1 type
        metadata_member_list = metadata_type.findall('sforce:members', ns)
        for metadata_member in metadata_member_list:
            if (metadata_name is not None and len(metadata_name.strip()) > 0):
                if metadata_name in changes and changes[metadata_name] is not None:
                    changes[metadata_name].add(metadata_member.text)
                else:
                    changes.update({metadata_name : set()})
                    changes[metadata_name].add(metadata_member.text)
    return changes
