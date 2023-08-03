import unittest
import clang.cindex
import sys
sys.path.append("..")
from dod import analyze_dod 


class TestAnalyzeCrtp(unittest.TestCase):
    def analyze_dod_test(self):   
        expected = {'Bar': [('count', 10000)]}
        out = analyze_dod("/home/alex/Desktop/Test2/Calculator.cpp", 
                            "/home/alex/Desktop/Test2/COVERAGE_OUT/Calculator.cpp.gcov", 1000)
        print(out)
        self.assertEqual(out, expected)

        

if __name__ == '__main__':
    out = analyze_dod("/home/alex/Desktop/Test2/Calculator.cpp", 
                            "/home/alex/Desktop/Test2/COVERAGE_OUT/Calculator.cpp.gcov", 10)
    print(out)