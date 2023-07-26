import os
import re
from collections import defaultdict

def get_class_attribute_access_counts(directory):
    class_attribute_counts = defaultdict(lambda: defaultdict(int))
    for filename in os.listdir(directory):
        if filename.endswith('.gcov') and not filename.startswith('main.cpp'):
            class_name = filename.split('.')[0]
            with open(os.path.join(directory, filename), 'r') as file:
                for line in file:
                    if 'get_' in line or 'set_' in line:
                        parts = line.split(':')
                        try:
                            count = int(parts[0].strip())
                        except ValueError: 
                            count = 0
                        function_part = parts[-1].strip()
                        try: 
                            function_part = function_part.replace("{", "")
                        except: 
                            continue
                        if function_part.startswith(('get_', 'set_')):
                            attribute_name = function_part.split('_')[-1].rstrip('()')
                            class_attribute_counts[class_name][attribute_name] += count
                            
    return class_attribute_counts

def add_comment(filename, class_name, attributes):
    # assuming the attribute is part of a class like "class MyClass"
    class_pattern = re.compile(f'class\s+{class_name}\s*\{{')
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    with open(filename, 'w') as file:
        for line in lines:
            if class_pattern.search(line):
                file.write(f'// Consider DOD for these attributes: {", ".join(attributes)}\n')
            file.write(line)

def main(directory):
    class_attribute_counts = get_class_attribute_access_counts(directory)
    for class_name, attribute_counts in class_attribute_counts.items():
        frequently_accessed_attributes = [attribute for attribute, count in attribute_counts.items() if count > 999]
        if frequently_accessed_attributes:
            for filename in os.listdir(directory):
                if filename == class_name + '.h':
                    add_comment(os.path.join(directory, filename), class_name, frequently_accessed_attributes)

if __name__ == '__main__':
    main('.')
