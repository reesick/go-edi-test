"""Sorting algorithms - Quick Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

int partition(TrackedArray& arr, int low, int high) {
    int pivot = arr.get(high);
    int i = low - 1;
    
    for (int j = low; j < high; j++) {
        if (arr.get(j) < pivot) {
            i++;
            arr.swap(i, j);
        }
    }
    arr.swap(i + 1, high);
    return i + 1;
}

void quick_sort_helper(TrackedArray& arr, int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quick_sort_helper(arr, low, pi - 1);
        quick_sort_helper(arr, pi + 1, high);
    }
}

void quick_sort(TrackedArray& arr) {
    quick_sort_helper(arr, 0, arr.size() - 1);
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    quick_sort(arr);
    arr.print_trace();
    return 0;
}"""

def extract_array(code):
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
    """Extract ALL functions before main()"""
    lines = full_code.split('\n')
    function_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('#') or stripped.startswith('using'):
            continue
        
        if 'int main()' in line or 'int main(' in line:
            break
        
        if stripped:
            function_lines.append(line)
    
    if not function_lines:
        return full_code
    
    return '\n'.join(function_lines)

def execute(params):
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name="quick_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
