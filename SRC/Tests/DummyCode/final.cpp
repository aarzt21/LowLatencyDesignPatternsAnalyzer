#include <string>
#include <random>
#include <vector>

class FooClass {
protected:
	float result;
	std::string name;
public:
	FooClass(std::string name) : result(0.0), name(name) {}
	
	std::vector<int> generate_random_data(int n, int low, int high, int seed) {
	    std::mt19937 gen(seed);
	    std::uniform_int_distribution<> distrib(low, high);
	
	    std::vector<int> data(n);
	    for(int i=0; i<n; ++i) data[i] = distrib(gen);
	
	    return data;
	}
	
	 virtual void calculate_result(std::vector<int> &data, bool incl_neg) {
	//USE CRTP for this entire class.
	//Use TBBE pattern for this method (bool incl_neg) is known at compile time.
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
	
	std::string get_name() {
	    return name;
	}
	
	float get_result() {
	    return result;
	}
	

};

class FooChild : public FooClass {
public:
	FooChild() : FooClass("child"){}
	
	 virtual void calculate_result(std::vector<int> &data, bool incl_neg) {
	//USE CRTP for this entire class.
	//Use TBBE pattern for this method (bool incl_neg) is known at compile time.
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
	

};
