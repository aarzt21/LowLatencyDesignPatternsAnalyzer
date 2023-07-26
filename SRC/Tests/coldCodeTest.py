import unittest
import clang.cindex
import sys
sys.path.append("..")
from coldCode import analyze_coldCode

class TestAnalyzeCrtp(unittest.TestCase):
    def test_analyze_coldCode(self):

        expected_out = {12: "WARNING: Cold block detected: THEN block has 0.1% of the if condition's execution count."}
        out = analyze_coldCode("DummyCode/myClassCold.cpp", "DummyCode/myClassCold.cpp.gcov")
        self.assertEqual(out, expected_out)

        

if __name__ == '__main__':
    unittest.main()