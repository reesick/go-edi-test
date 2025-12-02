"""Searching Algorithms - Sentinel Search"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

int sentinel_search(TrackedArray& arr, int target) {
    int n = arr.size();
    int last = arr.get(n - 1);
    
    // Set sentinel
    arr.set(n - 1, target);
    
    int i = 0;
    while (arr.get(i) != target) {
        i++;
    }
    
    // Restore last element
    arr.set(n - 1, last);
    
    if (i < n - 1 || arr.get(n - 1) == target) {
        return i;  // Found
    }
    
    return -1;  // Not found
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    int target = 8;
    int result = sentinel_search(arr, target);
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
    return [5, 2, 8, 1, 9, 3]

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
        function_name="sentinel_search",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
