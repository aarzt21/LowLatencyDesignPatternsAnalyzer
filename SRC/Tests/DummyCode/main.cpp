

#include <iostream>
#include "myClassCold.h"

using namespace std;



int main(){

    auto foo = Foo();

    foo.foo();

    cout << foo.get_result() << std::endl; 



    return 0; 
}


