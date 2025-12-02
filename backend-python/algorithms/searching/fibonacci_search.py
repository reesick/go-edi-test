"""Searching Algorithms - Fibonacci Search"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

int min(int a, int b) {
    return (a < b) ? a : b;
}

int fibonacci_search(TrackedArray& arr, int target) {
    int n = arr.size();
    
    // Initialize Fibonacci numbers
    int fib2 = 0;   // (m-2)th Fibonacci
    int fib1 = 1;   // (m-1)th Fibonacci  
    int fib = fib2 + fib1;  // mth Fibonacci
    
    // Find smallest Fibonacci >= n
    while (fib < n) {
        fib2 = fib1;
        fib1 = fib;
        fib = fib2 + fib1;
    }
    
    int offset = -1;
    
    while (fib > 1) {
        int i = min(offset + fib2, n - 1);
        int val = arr.get(i);
        
        if (val < target) {
            fib = fib1;
            fib1 = fib2;
            fib2 = fib - fib1;
            offset = i;
        } else if (val > target) {
            fib = fib2;
            fib1 = fib1 - fib2;
            fib2 = fib - fib1;
        } else {
            return i;  // Found
        }
    }
    
    if (fib1 && offset + 1 < n && arr.get(offset + 1) == target) {
        return offset + 1;
    }
    
    return -1;  // Not found
}

int main() {
    vector<int> data = {1, 2, 3, 5, 8, 9, 13, 21};  // Sorted array
    TrackedArray arr(data);
    int target = 13;
    int result = fibonacci_search(arr, target);
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
    return [1, 2, 3, 5, 8, 9, 13, 21]

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
        function_name="fibonacci_search",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
