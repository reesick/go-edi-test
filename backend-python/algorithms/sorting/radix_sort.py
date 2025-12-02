"""Sorting algorithms - Radix Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void counting_sort_for_radix(TrackedArray& arr, int exp) {
    int n = arr.size();
    vector<int> output(n);
    vector<int> count(10, 0);
    
    // Count occurrences
    for (int i = 0; i < n; i++) {
        int val = arr.get(i);
        count[(val / exp) % 10]++;
    }
    
    // Cumulative count
    for (int i = 1; i < 10; i++) {
        count[i] += count[i-1];
    }
    
    // Build output array
    for (int i = n-1; i >= 0; i--) {
        int val = arr.get(i);
        int digit = (val / exp) % 10;
        output[count[digit] - 1] = val;
        count[digit]--;
    }
    
    // Copy back
    for (int i = 0; i < n; i++) {
        arr.set(i, output[i]);
    }
}

void radix_sort(TrackedArray& arr) {
    int n = arr.size();
    if (n == 0) return;
    
    // Find max element
    int max_val = arr.get(0);
    for (int i = 1; i < n; i++) {
        int val = arr.get(i);
        if (val > max_val) {
            max_val = val;
        }
    }
    
    // Sort by each digit
    for (int exp = 1; max_val / exp > 0; exp *= 10) {
        counting_sort_for_radix(arr, exp);
    }
}

int main() {
    vector<int> data = {170, 45, 75, 90, 802, 24, 2, 66};
    TrackedArray arr(data);
    radix_sort(arr);
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
    
    return [170, 45, 75, 90, 802, 24, 2, 66]

def extract_function(full_code):
    """Extract function code (skip headers/main)"""
    lines = full_code.split('\n')
    function_lines = []
    in_function = False
    brace_count = 0
    skip_main = False
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('using'):
            continue
        if 'int main()' in line or 'int main(' in line:
            skip_main = True
            break
        
        if not in_function:
            if re.match(r'(void|int|bool)\s+\w+\s*\([^)]*\)\s*\{?', stripped):
                in_function = True
        
        if in_function:
            function_lines.append(line)
            brace_count += line.count('{')
            brace_count -= line.count('}')
            
            # Check if we finished one function but there might be more
            if brace_count == 0 and '{' in ''.join(function_lines):
                in_function = False
    
    return '\n'.join(function_lines)

def execute(params):
    """Execute radix sort"""
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name="radix_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
