"""Sorting algorithms - Heap Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void heapify(TrackedArray& arr, int n, int i) {
    int largest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;
    
    if (left < n && arr.get(left) > arr.get(largest))
        largest = left;
    
    if (right < n && arr.get(right) > arr.get(largest))
        largest = right;
    
    if (largest != i) {
        arr.swap(i, largest);
        heapify(arr, n, largest);
    }
}

void heap_sort(TrackedArray& arr) {
    int n = arr.size();
    
    // Build max heap
    for (int i = n / 2 - 1; i >= 0; i--)
        heapify(arr, n, i);
    
    // Extract elements from heap
    for (int i = n - 1; i > 0; i--) {
        arr.swap(0, i);
        heapify(arr, i, 0);
    }
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    heap_sort(arr);
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
    """Extract ALL functions before main() - fixed for multi-function algorithms"""
    lines = full_code.split('\n')
    function_lines = []
    found_main = False
    
    for line in lines:
        stripped = line.strip()
        
        # Skip headers and using statements
        if stripped.startswith('#') or stripped.startswith('using'):
            continue
        
        # Stop when we hit main()
        if 'int main()' in line or 'int main(' in line:
            found_main = True
            break
        
        # Add everything else (all helper functions)
        if stripped:  # Skip empty lines
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
        function_name="heap_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
