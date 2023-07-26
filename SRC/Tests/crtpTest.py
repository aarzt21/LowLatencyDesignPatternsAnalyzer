import unittest
import clang.cindex
import sys
sys.path.append("..")
from crtp import analyze_crtp 


class TestAnalyzeCrtp(unittest.TestCase):
    def test_analyze_crtp(self):
        # Provide the test C++ source code
        test_code = """
        class Base {
            virtual void foo() {}
        };

        class Derived : public Base {
            void foo() override {}
        };

        int main() {
            Base* b = new Derived;
            b->foo();
            delete b;
            return 0;
        }
        """

        # Call the function with the test code
        return analyze_crtp(test_code, 'dummy.cpp')


        

if __name__ == '__main__':
    obj = TestAnalyzeCrtp()
    print(obj.test_analyze_crtp())
