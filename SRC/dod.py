import os
import re
from collections import defaultdict

def analyze_dod(filename, gcov_filename, factor=2):
    class_attribute_counts = defaultdict(lambda: defaultdict(int))
    class_hot_attr = {}

    with open(gcov_filename, 'r') as gcov_file:
        for line in gcov_file:
            if 'get_' in line or 'set_' in line:
                parts = line.split(':')
                for w in parts: 
                    class_name_search = re.search(r'\b[A-Z]\w*', w)
                    if class_name_search:
                        class_name = class_name_search.group()

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

    # Add comment
    for class_name, attribute_counts in class_attribute_counts.items():
        min_count = min(attribute_counts.values())
        frequently_accessed_attributes = [(attribute, count) for attribute, count in attribute_counts.items() if count > factor * min_count]
        if frequently_accessed_attributes:
            class_hot_attr[class_name] = frequently_accessed_attributes
  
    return class_hot_attr
