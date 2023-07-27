import unittest
import clang.cindex
import sys
sys.path.append("..")
from dod import analyze_dod 


class TestAnalyzeCrtp(unittest.TestCase):
    def analyze_dod_test(self):   
        expected = {'Bar': [('count', 10000)]}
        out = analyze_dod("DummyCode/dummyDOD.cpp", 
                            "DummyCode/dummyDOD.cpp.gcov", 1000)
        
        self.assertEqual(out, expected)

        

if __name__ == '__main__':
    unittest.main()
