
#include "myClassCold.h"

int Foo::get_result(){
    return result; 
}

void Foo::foo(){
            int k = 1; 

            for(int i = 0; i < 100000; i++){
                if (i % 738 == 0){
                    k++;
                    k++;
                }
                k++;                
            }
            result = k; 

}