"""
    Install Salesforce CLI and append it to your environment path before running this script.
"""
import argparse
import logging
import os
import subprocess
import sys

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        alias - alias to set
        url - authorization URL (do not store in quotes)
    """
    parser = argparse.ArgumentParser(description='A script to authenticate to Salesforce.')
    parser.add_argument('-a', '--alias')
    parser.add_argument('-u', '--url')
    args = parser.parse_args()
    return args


def make_temp_file(url):
    """
        Function to create the temporary file with the URL
    """
    file_name = 'temp_file.txt'
    file = open(file_name, 'w', encoding='utf-8')
    file.write(url)
    file.close()
    return os.path.abspath(file_name)


def run_command(cmd):
    """
        Function to run the command using the native shell
    """
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError:
        sys.exit(1)


def main(alias, url):
    """
        Main function to authenticate to Salesforce.
    """
    # Create temporary file to store the URL
    url_file = make_temp_file(url)

    # Set all commands
    # Do not expose the URL in the logs
    commands = []
    commands.append(f'sfdx force:auth:sfdxurl:store --sfdxurlfile {url_file}'
                    f' --setalias {alias} --json > /dev/null')
    commands.append(f'sfdx force:config:set defaultusername={alias}')
    commands.append(f'sfdx force:config:set defaultdevhubusername={alias}')

    # Run each command one after the other
    for command in commands:
        logging.info(command)
        run_command(command)

    # Delete the temporary file
    os.remove(url_file)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.alias, inputs.url)
