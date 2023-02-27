"""
    The URL should be 'https://org.mysalesforce.com/services/data' depending on your
    Salesforce instance (org).
"""
import argparse
import json
import logging
import urllib.request

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        url - URL which contains all supported API versions
    """
    parser = argparse.ArgumentParser(description='A script to determine the latest API version.')
    parser.add_argument('-u', '--url')
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


def main(url):
    """
        Main function to return the latest API version.
    """
    latest_version = find_latest_version(url)

    logging.info('The latest API version is: %s', latest_version)
    # print the version to store in a variable set by the terminal
    print(latest_version)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.url)
