"""
    Required modules
"""
from xml.etree import ElementTree as et

# register_namespace only influences serialization, not search
# use both to search the XML (search for apex) and serialize the XML (combine & append element)
et.register_namespace('', 'http://soap.sforce.com/2006/04/metadata')
name_space = {'sforce': 'http://soap.sforce.com/2006/04/metadata'}

class XMLParser(object):
    """
        Class to parse Salesforce XMLs. (input - tuple)
    """
    def __init__(self, filenames):
        assert len(filenames) > 0, 'No filenames!'
        if len(filenames) > 1:
            # save all roots, in order, to be processed later
            self.roots = [et.parse(filename).getroot() for filename in filenames]
        else:
            # extract the single string from the tuple
            self.roots = et.parse(filenames[0]).getroot()

    def combine(self):
        """
            Function to combine XMLs
        """
        for root in self.roots[1:]:
            self.append_element(self.roots[0], root)
        # return the string representation
        return et.tostring(self.roots[0], encoding='unicode')

    def append_element(self, one, other):
        """
            This function adds elements of the other XML to the first XML file
            Does not overwrite contents.
        """
        for element in other:
            one.append(element)

    def search_for_apex(self):
        """
            This function searches the XML for types that require Apex tests.
        """
        # assume tests are not required by default
        tests = False
        # define types which require Apex tests
        apex_types = ['ApexClass', 'ApexTriggers']
        # loop through all metadata types until there is at least 1 type
        # that requires Apex tests, if any
        for metadata_type in self.roots.findall('sforce:types', name_space):
            metadata_name = metadata_type.find('sforce:name', name_space)
            if metadata_name.text in apex_types:
                tests = True
                break
        return tests
