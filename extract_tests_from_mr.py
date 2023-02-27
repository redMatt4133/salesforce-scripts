"""
    Module to extract require Apex test classes from the commit message.
    GitLab pre-defined variable - $CI_COMMIT_MESSAGE
    Change GitLab repository settings to include the Apex::::Apex regex
    in the Default Merge Request Description.
    Then, update the default merge commit message to include the merge request description.
"""
import re

def extract_tests(commit_msg):
    """
        Extract tests using a regular expression.
        Apex::define,tests,here::Apex
    """
    try:
        tests = re.search(r'Apex::(.*?)::Apex', commit_msg, flags=0).group(1)
    # if the regex doesn't have a match, it will return an attribute error.
    # you can either ignore it (pass) or return an error if Apex tests is required
    # in all cases.
    except AttributeError:
        tests = None
        pass
    return tests
