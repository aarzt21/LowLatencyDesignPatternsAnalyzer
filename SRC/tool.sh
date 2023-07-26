#!/bin/bash

set -e
set -u

# Check if the input string is provided as an argument
if [ $# -ne 1 ]; then
    echo "Usage: $0 '<input_files (.cpp)>' "
    exit 1
fi

# Assign the input files to a variable
input_files="$1"

# Check if the directory exists
if [ -d "Output" ]; then
    # If it does, delete the directory and its contents
    rm -rf Output
fi

# Recreate the directory
mkdir Output


cp $input_files Output #copy source files

# Copy corresponding header files into the Output folder
for file in $input_files
do
    base="${file%.cpp}"
    if [ -f "$base.h" ]
    then
        cp "$base.h" Output
    fi
done


cd Output


# Compile all input files into a single executable with g++ using the specified options
output_file="output"
g++ -fprofile-arcs -ftest-coverage -o $output_file $input_files

# Run the executable program
./$output_file

# Run gcov on each .cpp file, appending the output to gcov.log
for input_file in *.cpp
do
    gcov output-$input_file > /dev/null 2>&1
done


# For each file in the directory
for file in *
do
    # If the file is not a .cpp file and is not a corresponding .gcov file of a .cpp file
    if [[ $file != *.cpp && ! ( $file == *.gcov && -f "${file%.gcov}" ) ]]; then
        rm "$file"
    fi
done

cp ../*.h .

# For every .gcov file in the current directory...
for filename in *.cpp
do
  python3 ../coldCode.py "$filename" | python3 ../tbbElim.py | python3 ../crtpDetector.py "$filename"
done



echo "Analysis successful. Results can be found in 'Output' folder."

