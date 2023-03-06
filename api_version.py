"""
    The URL should be 'https://org.mysalesforce.com/services/data' depending on your
    Salesforce instance (org).
    This script can be ran as a scheduled pipeline to periodically check and update 
    the sfdx-project.json file with the latest API version.
"""
import argparse
import json
import logging
import os
import sys
import urllib.request

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        url - URL which contains all supported API versions
        file - sfdx-project.json
    """
    parser = argparse.ArgumentParser(description='A script to determine the latest API version.')
    parser.add_argument('-u', '--url')
    parser.add_argument('-f', '--file', default='./sfdx-project.json')
    args = parser.parse_args()
    return args


def find_latest_version(salesforce_url):
    """
        Function to open the URL as a JSON and
        find the latest API version.
    """
    with urllib.request.urlopen(salesforce_url) as json_file:
        json_data = json.loads(json_file.read().decode('utf8'))

    # add all versions to an array
    api_versions = []
    for element in json_data:
        # convert to float due to decimal
        api_verison = float(element['version'])
        api_versions.append(api_verison)
    # return latest version
    return max(api_versions)


def update_json_file(latest_version, json_path):
    """
        Function to update the JSON file with
        the latest API version.
    """
    with open(os.path.abspath(json_path), encoding='utf-8') as json_file:
        parsed_json = json.load(json_file)

    source_api_version = parsed_json.get('sourceApiVersion')
    if source_api_version:
        # convert the latest version (float) to a string
        if str(latest_version) == source_api_version:
            logging.info('The JSON file already has the latest API version.')
            sys.exit(1)
        else:
            logging.info('Updating the JSON file to have the latest API version.')
            parsed_json['sourceApiVersion'] = f"{latest_version}"

        with open(os.path.abspath(json_path), 'w', encoding='utf-8') as json_file:
            json.dump(parsed_json, json_file, indent=4, sort_keys=True)
    else:
        # sourceApiVersion is optional
        logging.warning('Source API version not found in the JSON file.')
        sys.exit(1)


def main(url, json_file):
    """
        Main function to return the latest API version
        and update the JSON file.
    """
    latest_api_version = find_latest_version(url)
    logging.info('The latest API version is: %s', latest_api_version)
    # Print variable so it can be stored in a variable
    print(latest_api_version)
    update_json_file(latest_api_version, json_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.url, inputs.file)
