"""Sorting algorithms - Bubble Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void bubble_sort(TrackedArray& arr) {
    int n = arr.size();
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr.get(j) > arr.get(j+1)) {
                arr.swap(j, j+1);
            }
        }
    }
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    bubble_sort(arr);
    arr.print_trace();
    return 0;
}"""

def extract_array(code):
    """Extract array values from user code"""
    patterns = [
        r'vector<int>\s+\w+\s*=\s*\{([^}]+)\}',
        r'vector<int>\s+\w+\s*\{([^}]+)\}',
        r'int\s+\w+\[\]\s*=\s*\{([^}]+)\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            numbers_str = match.group(1)
            numbers = [int(x.strip()) for x in numbers_str.split(',') 
                      if x.strip().isdigit() or (x.strip().lstrip('-').isdigit())]
            if numbers:
                return numbers
    
    return [5, 2, 8, 1, 9, 3]

def extract_function(full_code):
    """Extract function code (skip headers/main)"""
    lines = full_code.split('\n')
    function_lines = []
    in_function = False
    brace_count = 0
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('using'):
            continue
        if 'int main()' in line or 'int main(' in line:
            break
        
        if not in_function:
            if re.match(r'(void|int|bool)\s+\w+\s*\([^)]*\)\s*\{?', stripped):
                in_function = True
        
        if in_function:
            function_lines.append(line)
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            if brace_count == 0 and '{' in ''.join(function_lines):
                break
    
    return '\n'.join(function_lines)

def execute(params):
    """Execute bubble sort"""
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name="bubble_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
