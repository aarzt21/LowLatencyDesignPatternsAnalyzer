

#include <iostream>
#include "dummyDOD.h"
using namespace std;


int main()
{

    auto obj = Bar();

    for (int i = 0; i < 10000; i++)
        int k = obj.get_count();
    
    cout << "Done" << endl; 


    return 0; 
}