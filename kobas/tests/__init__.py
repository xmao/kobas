import os, unittest, traceback
from xml.sax import saxutils

def get_test_data(path):
    return open(os.path.join(get_test_data_dir(), path))

def get_test_data_dir():
    return os.path.join(os.path.join(
        os.path.dirname(__file__), 'data', ))

class KEGGTestCase(unittest.TestCase):
    """build KEGGTestCase by simulating ZopeTestCase"""

    def setUp(self):
        self.handle = saxutils.XMLGenerator()

    def get_fields(self, sec_name):
        """return all the content of sec_name field in the test file
        """
        section, sections = [], []
        i, is_in_section = 0, False
        while i < len(self.lines):
            if self.lines[i][:len(sec_name)] == sec_name:
                sections.append([self.lines[i]])
                i += 1
                while self.lines[i][0] == ' ':
                    sections[-1].append(self.lines[i])
                    i += 1
            i += 1
        return  ["".join(section) for section in sections]

    def parse(self, format, istream):
        parser = format.make_parser()
        try:
            parser.parseString(istream)
        except:
            traceback.print_exc()
            self.fail()
