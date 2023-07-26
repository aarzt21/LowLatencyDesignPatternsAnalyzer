import unittest
import clang.cindex
import sys
sys.path.append("..")
from tbbe import analyze_tbbe 

class TestAnalyzeTbbe(unittest.TestCase):
    def test_analyze_tbbe(self):
        test_code = """
        int foo(int x) {
            if (x > 0) {
                return x + 1;
            } else {
                return x - 1;
            }
        }

        int main() {
            int a = 5;
            foo(a);
            return 0;
        }
        """

        expected_output = """
        // This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.
        int foo(int x) {
            if (x > 0) {
                return x + 1;
            } else {
                return x - 1;
            }
        }

        int main() {
            int a = 5;
            foo(a);
            return 0;
        }
        """

        analyzed_code = analyze_tbbe(test_code, 'dummy.cpp')

        return analyzed_code

if __name__ == '__main__':
    obj = TestAnalyzeTbbe()
    print(obj.test_analyze_tbbe())
