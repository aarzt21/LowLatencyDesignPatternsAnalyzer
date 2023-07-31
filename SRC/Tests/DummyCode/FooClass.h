//
// Created by alex on 27.07.23.
//

#ifndef TEST_FOOCLASS_H
#define TEST_FOOCLASS_H


#include <string>
#include <random>
#include <vector>

class FooClass {
protected:
    float result;
    std::string name;

public:
    FooClass(std::string name);;

    std::vector<int> generate_random_data(int n, int low, int high, int seed);

    virtual void calculate_result(std::vector<int>& data, bool incl_neg);

    std::string get_name();

    float get_result();
};


class FooChild: public FooClass {
public:
    FooChild();
    void calculate_result(std::vector<int> &data, bool incl_neg) override;

};



#endif //TEST_FOOCLASS_H
