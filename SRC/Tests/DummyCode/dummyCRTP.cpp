
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
        