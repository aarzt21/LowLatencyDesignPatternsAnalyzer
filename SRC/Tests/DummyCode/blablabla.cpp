//
// Created by alex on 27.07.23.
//

#include "FooClass.h"

std::vector<int> FooClass::generate_random_data(int n, int low, int high, int seed) {
    std::mt19937 gen(seed);
    std::uniform_int_distribution<> distrib(low, high);

    std::vector<int> data(n);
    for(int i=0; i<n; ++i) data[i] = distrib(gen);

    return data;
}

FooClass::FooClass(std::string name) : result(0.0), name(name) {}

void FooClass::calculate_result(std::vector<int> &data, bool incl_neg) {
// WARNING: Virtual method 'calculate_result(std::vector<int> &, bool)'. Consider using the Curiously Recurring Template Pattern (CRTP) instead.
//This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.
    int sum = 0;
    int count = 0;

    if (incl_neg){
        for (auto& e : data){
            sum += e;
        }
        result = sum/data.size();
        return;
    }
    else {
        for (auto& e : data){
            sum += e;
            count++;
        }
        result = sum/count;
        return;
    }

}

std::string FooClass::get_name() {
    return name;
}

float FooClass::get_result() {
    return result;
}

void FooChild::calculate_result(std::vector<int> &data, bool incl_neg) {
// WARNING: Virtual method 'calculate_result(std::vector<int> &, bool)'. Consider using the Curiously Recurring Template Pattern (CRTP) instead.
//This function uses an argument in one of its branches -> if the argument is known at compile time then consider the TBBE Pattern.
    int sum = 0;
    int count = 0;

    if (incl_neg){
        for (auto& e : data){
            sum += e;
        }
        result = sum/data.size() + 10;
        return;
    }
    else {
        for (auto& e : data){
            sum += e;
            count++;
        }
        result = sum/count + 10;
        return;
    }

}

FooChild::FooChild() : FooClass("child"){}
