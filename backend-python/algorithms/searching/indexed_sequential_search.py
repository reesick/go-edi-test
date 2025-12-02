"""Searching Algorithms - Indexed Sequential Search"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

int indexed_sequential_search(TrackedArray& arr, int target) {
    int n = arr.size();
    int jump = sqrt(n);  // Index jump size
    int prev = 0;
    
    // Jump through indices
    while (prev < n && arr.get(min(jump, n) - 1) < target) {
        prev = jump;
        jump += sqrt(n);
        
        if (prev >= n) {
            return -1;  // Not found
        }
    }
    
    // Linear search in block
    for (int i = prev; i < min(jump, n); i++) {
        if (arr.get(i) == target) {
            return i;  // Found
        }
    }
    
    return -1;  // Not found
}

int main() {
    vector<int> data = {1, 2, 3, 5, 8, 9};  // Sorted array
    TrackedArray arr(data);
    int target = 5;
    int result = indexed_sequential_search(arr, target);
    arr.print_trace();
    return 0;
}"""

def extract_array(code):
    patterns = [
        r'vector<int>\s+\w+\s*=\s*\{([^}]+)\}',
        r'int\s+\w+\[\]\s*=\s*\{([^}]+)\}',
    ]
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            numbers_str = match.group(1)
            numbers = [int(x.strip()) for x in numbers_str.split(',') 
                      if x.strip().lstrip('-').isdigit()]
            if numbers:
                return numbers
    return [1, 2, 3, 5, 8, 9]

def extract_function(full_code):
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
    
    return '\n'.join(function_lines) if function_lines else full_code

def execute(params):
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="searching",
        function_name="indexed_sequential_search",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
