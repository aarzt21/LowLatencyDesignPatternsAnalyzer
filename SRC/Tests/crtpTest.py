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

        with open("DummyCode/dummyCRTP.cpp", "w") as file:
            file.write(test_code)

        expected_out = {3: "WARNING: Virtual method 'foo()'. Consider using the Curiously Recurring Template Pattern (CRTP) instead.", 7: "WARNING: Virtual method 'foo()'. Consider using the Curiously Recurring Template Pattern (CRTP) instead.", 
                        12: "WARNING: Virtual method 'foo'. Consider using the Curiously Recurring Template Pattern (CRTP) instead."}
        out = analyze_crtp("DummyCode/dummyCRTP.cpp")
        self.assertEqual(out, expected_out)

        

if __name__ == '__main__':
    unittest.main()
