import unittest
import clang.cindex
import sys
sys.path.append("..")
from tbbe import analyze_tbbe 

class TestAnalyzeTbbe(unittest.TestCase):
    def test_analyze_tbbe_function(self):
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

        with open("dummy.cpp", 'w') as file: 
            file.write(test_code)

        expected_output = {2: 'This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.'}

        analyzed_code = analyze_tbbe('DummyCode/dummy.cpp')

        self.assertEqual(analyzed_code, expected_output)

    def test_analyze_tbbe_class_method(self):
        test_code = """
        class Foo {
            int bar(int x) {
                if (x > 0) {
                    return x + 1;
                } else {
                    return x - 1;
                }
            }
        };
        """


        with open("dummy_class.cpp", 'w') as file: 
            file.write(test_code)

        expected_output = {3: 'This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.'}

        analyzed_code = analyze_tbbe('DummyCode/dummy_class.cpp')

        self.assertEqual(analyzed_code, expected_output)

if __name__ == '__main__':
    unittest.main()
