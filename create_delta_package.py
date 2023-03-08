"""
    Salesforce delta package script.
    Uses the GitLab API to take the diff of two commits.
"""
import argparse
import json
import logging
import os
import urllib.request

# import local scripts
import check_package_dir
import merge_manual_package
import metadata_types
import package_template

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        from_ref - previous commit or baseline branch ($CI_COMMI_SHA_BEFORE)
        to_ref - current commit or branch ($CI_COMMIT_SHA)
        authenticate - access token for the API call
        server - $CI_SERVER_HOST
        id - $CI_PROJECT_ID
        json - sfdx-project.json
    """
    parser = argparse.ArgumentParser(description='A script to determine the latest API version.')
    parser.add_argument('-f', '--from_ref')
    parser.add_argument('-t', '--to_ref')
    parser.add_argument('-a', '--authenticate')
    parser.add_argument('-s', '--server')
    parser.add_argument('-i', '--id')
    parser.add_argument('-j', '--json', default='./sfdx-project.json')
    args = parser.parse_args()
    return args


def api_request(source_ref, to_ref, auth, project_server, project_id):
    """
        Function to open the URL and load as a JSON
    """
    # set up the GitLab API request
    repo_url = f'https://{project_server}/api/v4/projects/{project_id}/repository/'
    compare_url = repo_url + f"compare?from={source_ref}&to={to_ref}"
    headers = {"PRIVATE TOKEN": auth}

    # make the API request and parse as a JSON
    req = urllib.request.Request(compare_url, headers=headers)
    with urllib.request.urlopen(req) as json_file:
        data = json.loads(json_file.read().decode('utf8'))
    return data


def parse_json_response(diff_data):
    """
        Append all changed files to an array.
    """
    logging.info('New and modified files:')
    new_files = []
    for diff in diff_data["diffs"]:
        logging.info(diff['new_path'])
        new_files.append(diff['new_path'])
    return new_files


def find_metadata_file(changed_files, json_file):
    """
        Determine which changed files are Salesforce metadata
        Use the check_package_dir script
    """
    source_folder = check_package_dir.main(json_file)
    metadata_changes = []
    for change_file in changed_files:
        if source_folder in change_file:
            metadata_changes.append(change_file)
    return metadata_changes


def find_component_types(file_path):
    """
        find the component type using the imported
        dictionary
    """
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    subdirname = os.path.basename(os.path.dirname(file_path))

    component_type = ''
    member = ''

    # iterate over all keys in the dict
    # value un-used but declared to remove Pylint suggestion
    # "consider-using-dict-items / C0206 - Consider iterating with .items()"
    for key, value in metadata_types.metadata_Types.items():
        search_for = '/' + key + '/'
        if search_for in file_path:
            component_type = metadata_types.metadata_Types[key]
            member = name.split('.')[0]
        # include the parent folder for specific items as noted in the dict
        if component_type in metadata_types.inside_Folder:
            member = subdirname + os.sep + name.split('.')[0]
    return (component_type, member, ext, file_path)


def build_type_items(file_list):
    """
        build the type items
    """
    changed = {}
    for filename in file_list:
        (component_type, member, ext, file_path) = find_component_types(filename)
        if (component_type is not None and len(component_type.strip()) > 0) :
            if component_type in changed and changed[component_type] is not None:
                changed[component_type].add(member)
            else:
                changed.update({component_type : set()})
                changed[component_type].add(member)
    return changed


def create_package_xml(items):
    """
        create the package.xml file
    """
    # initialize the package with the header
    package_contents = package_template.PACKAGE_HEADER

    # append each item to the package, if any
    for key in items:
        package_contents += "\t<types>\n"
        package_contents += "\t\t<name>" + key + "</name>\n"
        for member in items[key]:
            package_contents += "\t\t<members>" + member + "</members>\n"
        package_contents += "\t</types>\n"
    # append the footer
    package_contents += package_template.PACKAGE_FOOTER
    package_path = 'package.xml'
    logging.info('Delta package:')
    logging.info(package_contents)
    with open(package_path, 'w', encoding='utf-8') as package_file:
        package_file.write(package_contents)


def main(from_ref, to_ref, auth, project_server, project_id, json_file):
    """
        Main function to take the diff and build the package.xml
    """
    response = api_request(from_ref, to_ref, auth, project_server, project_id)
    updated_files = parse_json_response(response)
    metadata_files = find_metadata_file(updated_files, json_file)
    changed = build_type_items(metadata_files)
    # import and merge manual package.xml with auto delta XML if desired
    changed = merge_manual_package.parse_manual_package('manifest/package.xml', changed)
    create_package_xml(changed)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.from_ref, inputs.to_ref, inputs.authenticate,
         inputs.server, inputs.id, inputs.json)
