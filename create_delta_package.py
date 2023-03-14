"""
    Script which takes the git diff and
    creates the package.xml
    Requires Git Bash.
"""
import argparse
import json
import logging
import os
import re
import subprocess

# import local scripts
import custom_labels
import check_package_dir
import merge_manual_package
import metadata_types
import package_template

# Format logging message
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to pass required arguments.
        from_ref - previous commit or baseline branch $CI_COMMIT_BEFORE_SHA
        to_ref - current commit or new branch $CI_COMMIT_SHA
        json - sfdx-project.json
        delta - delta file created by this script
        manifest - manual manifest file to merge with delta
    """
    parser = argparse.ArgumentParser(description='A script to generate the delta package.')
    parser.add_argument('-f', '--from_ref')
    parser.add_argument('-t', '--to_ref')
    parser.add_argument('-j', '--json', default='./sfdx-project.json')
    parser.add_argument('-d', '--delta', default='delta.xml')
    parser.add_argument('-m', '--manifest', default='manifest/package.xml')
    args = parser.parse_args()
    return args


def take_git_diff(from_ref, to_ref):
    """
        Function to take the diff and create
        a dictionary of changes.
    """
    # Take the diff and store the output
    command = f'git diff {from_ref}..{to_ref}'
    output = subprocess.run(command, stdout=subprocess.PIPE, universal_newlines=True,
                            check=True, shell=True)

    # Split the output into a list of file diffs
    file_diffs = output.stdout.strip().split('diff --git ')

    # Define an empty dictionary to store the changed files
    changed_files = {}

    for file_diff in file_diffs[1:]:
        # Extract the file name from the diff
        file_name = file_diff.split('\n')[0].split(' b/')[1]
        # Add the file diff to the dictionary
        changed_files[file_name] = file_diff
    return changed_files


def find_metadata_files(changed_files, json_file):
    """
        Determine metadata source folder with other script
        and then confirm changed files are inside that path
    """
    source_folder = check_package_dir.main(json_file)
    metadata_changes = []
    for change_file in changed_files.items():
        # if source folder is in the key, append the file
        if source_folder in change_file[0]:
            metadata_changes.append(change_file[0])
    return metadata_changes


def find_component_type(file_path, diffs):
    """
        Find the component type using 
        the imported dictionary
    """
    #dir_name = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    # split base name by name and extension
    # not using "name, ext = os.path.splittext" since we
    # don't need to use the file extension at the moment
    name_ext = os.path.splitext(base_name)
    subdirname = os.path.basename(os.path.dirname(file_path))

    component_type = ''
    member = ''

    # iterate through all keys in the dictionary
    # using .items() to remove Pylint suggestion over .keys()
    # "consider-using-dict-items / C0206 - Consider iterating with .items()"
    for keyvalue in metadata_types.metadata_Types.items():
        key = keyvalue[0]
        search_for = '/' + key + '/'
        if search_for in file_path:
            component_type = metadata_types.metadata_Types[key]
            member = (name_ext[0].split('.')[0],)
        # Include the parent folder for specific items
        if component_type in metadata_types.inside_Folder:
            member =  (subdirname + os.sep + name_ext[0].split('.')[0],)
        # If the component type has child items, check if metadata falls under
        # the child item and overwrite the component type if it does
        if component_type in metadata_types.has_child_Items:
            for child_types in metadata_types.has_child_Items[component_type]:
                if child_types.get(subdirname):
                    component_type = child_types[subdirname]
                    # find the parent object to append to member name
                    parent_object = re.search(fr"{search_for}(\w+)/", file_path).group(1)
                    member = (f'{parent_object}.{member[0]}',)
                    break
        # Check inside the file for specific items
        if component_type in metadata_types.inside_File:
            component_type, member = custom_labels.parse_custom_labels(file_path, diffs)
    return (component_type, member)


def build_type_items(file_list, diffs):
    """
        Build type items.
    """
    changed = {}
    for filename in file_list:
        (component_type, member) = find_component_type(filename, diffs)
        if (component_type is not None and len(component_type.strip()) > 0) :
            # if member tuple is greater than 1, add the first 1 by setting the type
            # then, add the remaining items
            if len(member) > 1:
                changed.update({component_type : set()})
                changed[component_type].add(member[0])
                for member_item in member[1:]:
                    changed[component_type].add(member_item)
            elif component_type in changed and changed[component_type] is not None:
                for member_item in member:
                    changed[component_type].add(member_item)
            else:
                for member_item in member:
                    changed.update({component_type : set()})
                    changed[component_type].add(member_item)
    return changed


def create_package_xml(items, delta_file):
    """
        Create the package.xml file
    """
    # Initialize the package contents with the header
    package_contents = package_template.PKG_HEADER

    # Append each item to the package
    #    <types>
    #       <name>ApexClass</name>
    #       <members>ProjectTaskTriggerHandler</members>
    #    </types>
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
    with open(delta_file, 'w', encoding='utf-8') as package_file:
        package_file.write(package_contents)


def main(source, to_ref, json_file, delta, manifest):
    """
        Main function to take the diff and
        build the package.xml file.
    """
    updated_files = take_git_diff(source, to_ref)
    metadata_files = find_metadata_files(updated_files, json_file)
    changed = build_type_items(metadata_files, updated_files)
    # merge manual package.xml if required
    changed = merge_manual_package.parse_manual_package(manifest, changed)
    create_package_xml(changed, delta)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.from_ref, inputs.to_ref,
         inputs.json, inputs.delta, inputs.manifest)
