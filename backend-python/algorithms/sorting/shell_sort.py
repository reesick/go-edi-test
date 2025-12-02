"""Sorting algorithms - Shell Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void shell_sort(TrackedArray& arr) {
    int n = arr.size();
    
    // Start with a big gap, then reduce
    for (int gap = n/2; gap > 0; gap /= 2) {
        // Do insertion sort for this gap size
        for (int i = gap; i < n; i++) {
            int temp = arr.get(i);
            int j;
            
            for (j = i; j >= gap && arr.get(j - gap) > temp; j -= gap) {
                arr.set(j, arr.get(j - gap));
            }
            
            arr.set(j, temp);
        }
    }
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    shell_sort(arr);
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
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name="shell_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
