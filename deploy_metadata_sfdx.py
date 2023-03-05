"""
    Install Salesforce CLI and append it to your environment path before running this script.
"""
import argparse
import logging
import re
import subprocess
import sys
import threading

# format logger
logging.basicConfig(format='%(message)s', level=logging.DEBUG)


def parse_args():
    """
        Function to parse required arguments.
        tests - required Apex tests to run against
        manifest - path to the package.xml file
        wait - number of minutes to wait for command to complete
        environment - Salesforce environment URL
        log - deploy log where the output of this script is being written to
            python ./deploy_metadata_sfdx.py --args | tee -a deploy_log.txt
            -a flag required to append to file during run-time
        validate - set to True to run validation only deployment (for quick deploys)
        debug - print command rather than run
    """
    parser = argparse.ArgumentParser(description='A script to authenticate to Salesforce.')
    parser.add_argument('-t', '--tests')
    parser.add_argument('-m', '--manifest', default='manifest/package.xml')
    parser.add_argument('-w', '--wait', default=33)
    parser.add_argument('-e', '--environment')
    parser.add_argument('-l', '--log', default='deploy_log.txt')
    parser.add_argument('-v', '--validate', default=False, action='store_true')
    parser.add_argument('-d', '--debug', default=False, action='store_true')
    args = parser.parse_args()
    return args


def create_sf_link(sf_env, log):
    """
        Function to check the deploy log for the ID
        and build the URL.
    """
    pattern = r'Deploy ID: (.*)'
    classic_sf_path = '/changemgmt/monitorDeploymentsDetails.apexp?retURL=' +\
                        '/changemgmt/monitorDeployment.apexp&asyncId='

    # keep reading the log until the ID has been found
    with open(log, 'r', encoding='utf-8') as deploy_file:
        while True:
            file_line = deploy_file.readline()
            match = re.search(pattern, file_line)
            # if regex is found, build the link and break the loop
            if match:
                deploy_id = match.group(1)
                sf_id = deploy_id[:-3]
                deploy_url = sf_env + classic_sf_path + sf_id
                logging.info(deploy_url)
                break


def run_command(cmd):
    """
        Function to run the command using the native shell
    """
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as exception:
        # store the exception in the thread object
        threading.current_thread().exc = exception


def remove_spaces(string):
    """
        Function to remove all spaces in a string.
    """
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', string)


def main(tests, manifest, wait, environment, log, validate, debug):
    """
        Main function to deploy metadata to Salesforce.
    """
    # Define the command
    if tests and not tests.isspace():
        tests = remove_spaces(tests)
        command = (f'sfdx force:source:deploy -m {manifest} -l RunSpecifiedTests'
                    f' -r "{tests}" -w {wait} --verbose')
    else:
        command = (f'sfdx force:source:deploy -m {manifest} -l RunSpecifiedTests'
                   f' -r "not,a,test" -w {wait} --verbose')

    # Append '-c' flag to run a validation deployment
    if validate:
        command += ' -c'

    if not debug:
        logging.info(command)
        # create and start threads
        read_thread = threading.Thread(target=create_sf_link, args=(environment, log))
        deploy_thread = threading.Thread(target=run_command, args=(command,))
        read_thread.start()
        deploy_thread.start()

        # wait for deploy to finish
        deploy_thread.join()

        # kill read thread if it's still running
        # ex: if package.xml is empty, no ID is created
        if read_thread.is_alive():
            read_thread.terminate()

        # exit with error if exception attribute is found
        if hasattr(deploy_thread, 'exc'):
            sys.exit(1)
    else:
        print(command)


if __name__ == '__main__':
    inputs = parse_args()
    main(inputs.tests, inputs.manifest, inputs.wait, inputs.environment,
         inputs.log, inputs.validate, inputs.debug)
