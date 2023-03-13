"""
  This script uses the SFDX git delta plugin to create the delta
  package. Then, it combines the delta XML file with the manual
  manifest XML file to create the combined XML file.
"""
import argparse
import logging
import re
import subprocess
import xml.etree.ElementTree as ET

# import local script
import package_template

# Format logging message
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
# register the namespace to search the XML
ns = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}


def parse_args():
    """
        Parse the required args
        from_ref - previous commit or baseline branch $CI_COMMIT_BEFORE_SHA
        to_ref - current commit or new branch $CI_COMMIT_SHA
        delta - delta file created by the SDFX Git Delta Plugin
            default file created by plugin is package/package.xml 
        manifest - manual manifest file in this repo
        combined - package.xml with delta and manifest updates combined
    """
    parser=argparse.ArgumentParser(description='A script to build the package.xml')
    parser.add_argument('-f', '--from_ref')
    parser.add_argument('-t', '--to_ref')
    parser.add_argument('-d', '--delta', default='package/package.xml')
    parser.add_argument('-m', '--manifest', default='manifest/package.xml')
    parser.add_argument('-c', '--combined', default='delta.xml')
    args=parser.parse_args()
    return args


def parse_package_file(package_path, changes):
    """
        Parse the package.xml file
        and append the metadata types
        to the existing changes dictionary
    """
    root = ET.parse(package_path).getroot()

    for metadata_type in root.findall('sforce:types', ns):
        metadata_name = (metadata_type.find('sforce:name', ns)).text
        # find all matches if there are multiple members for 1 metadata type
        metadata_member_list = metadata_type.findall('sforce:members', ns)
        for metadata_member in metadata_member_list:
            # if a wilcard is present in the member, don't process it
            wildcard = re.search(r'\*', metadata_member.text)
            if (metadata_name is not None and wildcard is None and len(metadata_name.strip()) > 0) :
                if metadata_name in changes and changes[metadata_name] is not None:
                    changes[metadata_name].add(metadata_member.text)
                else:
                    changes.update({metadata_name : set()})
                    changes[metadata_name].add(metadata_member.text)
            elif wildcard:
                logging.warning('WARNING: Wildcards are not allowed in the package.xml')
    return changes


def run_command(command):
    """
        Run the command using the system's command prompt (shell=True)
    """
    subprocess.run(command, shell=True, check=True)


def create_changes_dict(from_ref, to_ref, delta, manifest):
    """
        Run the plugin to create the delta file
        and add the changes from the delta file and manifest file
        to a dictionary.
    """
    plugin_command = f'sfdx sgd:source:delta --to "{to_ref}" --from "{from_ref}" --output "."'
    run_command(plugin_command)
    # initialize changes dictionary
    changed = {}
    changed = parse_package_file(delta, changed)
    changed = parse_package_file(manifest, changed)
    return changed


def create_package_xml(items, output_file):
    """
        Create the final package.xml file
    """
    # Initialize the package contents with the header
    package_contents = package_template.PKG_HEADER

    # Append each item to the package
    for key in items:
        package_contents += "\t<types>\n"
        for member in items[key]:
            package_contents += "\t\t<members>" + member + "</members>\n"
        package_contents += "\t\t<name>" + key + "</name>\n"
        package_contents += "\t</types>\n"
    # Append the footer to the package
    package_contents += package_template.PKG_FOOTER
    logging.info('Auto-generated delta package:')
    logging.info(package_contents)
    with open(output_file, 'w', encoding='utf-8') as package_file:
        package_file.write(package_contents)


def main(from_ref, to_ref, delta, manifest, combined):
    """
        Main function to build the delta package
    """
    changes = create_changes_dict(from_ref, to_ref, delta, manifest)
    create_package_xml(changes, combined)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.from_ref, inputs.to_ref,
         inputs.delta, inputs.manifest, inputs.combined)
