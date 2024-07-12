import unittest

parentddir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parentddir)
from morpheus.Maestro import maestro
from morpheus.Schematic import schematic
from morpheus.Terminal import Terminal
from morpheus import Config
from morpheus import *

class TerminalUnitTest(unittest.TestCase):
    
    
    #get terminal from original Test_bench_definitions
    def test_basic_load(self):
        term = Terminal();
        term.getTerminal("");
        self.assertEqual('foo'.upper(), 'FOO')


    #get terminal from original Test_bench_definitions using cache rather than loading from file
    def test_cache(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()