"""
    Install Salesforce CLI and append it to your environment path before running this script.
"""
import argparse
import logging
import re
import subprocess
import sys

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        tests - required Apex tests to run against
        manifest - path to the package.xml file
        wait - number of minutes to wait for command to complete
        validate - set to True to run validation only deployment (for quick deploys)
        debug - print command rather than run
    """
    parser = argparse.ArgumentParser(description='A script to authenticate to Salesforce.')
    parser.add_argument('-t', '--tests')
    parser.add_argument('-m', '--manifest', default='manifest/package.xml')
    parser.add_argument('-w', '--wait', default=33)
    parser.add_argument('-v', '--validate', default=False, action='store_true')
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    args = parser.parse_args()
    return args


def run_command(cmd):
    """
        Function to run the command using the native shell
    """
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError:
        logging.warning('Deployment failed. Check the lines above for the error.')
        sys.exit(1)


def remove_spaces(string):
    """
        Function to remove all spaces in a string.
    """
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)


def main(tests, manifest, wait, validate, debug):
    """
        Main function to authenticate to Salesforce.
    """
    # Define the command
    if tests and not tests.isspace():
        tests = remove_spaces(tests)
        command = f'sfdx force:source:deploy -m {manifest} -l RunSpecifiedTests -r {tests} -w {wait} --verbose'
    else:
        command = f'sfdx force:source:deploy -m {manifest} -l RunSpecifiedTests -r "not,a,test" -w {wait} --verbose'

    # Append '-c' flag to run a validation deployment
    if validate:
        command = command + ' -c'

    # Run the command
    if not debug:
        logging.info(command)
        run_command(command)
    else:
        print(command)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.tests, inputs.manifest, inputs.wait, inputs.validate, inputs.debug)
