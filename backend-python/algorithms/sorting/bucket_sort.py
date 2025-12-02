"""Sorting algorithms - Bucket Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void bucket_sort(TrackedArray& arr) {
    int n = arr.size();
    if (n == 0) return;
    
    // Find min and max
    int min_val = arr.get(0);
    int max_val = arr.get(0);
    for (int i = 1; i < n; i++) {
        int val = arr.get(i);
        if (val < min_val) min_val = val;
        if (val > max_val) max_val = val;
    }
    
    // Create buckets
    int bucket_count = n;
    vector<vector<int>> buckets(bucket_count);
    
    // Distribute elements into buckets
    for (int i = 0; i < n; i++) {
        int val = arr.get(i);
        int bucket_idx = (bucket_count - 1) * (val - min_val) / (max_val - min_val + 1);
        buckets[bucket_idx].push_back(val);
    }
    
    // Sort each bucket and merge
    int index = 0;
    for (int i = 0; i < bucket_count; i++) {
        // Simple insertion sort for each bucket
        for (int j = 1; j < buckets[i].size(); j++) {
            int key = buckets[i][j];
            int k = j - 1;
            while (k >= 0 && buckets[i][k] > key) {
                buckets[i][k+1] = buckets[i][k];
                k--;
            }
            buckets[i][k+1] = key;
        }
        
        // Copy bucket to array
        for (int j = 0; j < buckets[i].size(); j++) {
            arr.set(index++, buckets[i][j]);
        }
    }
}

int main() {
    vector<int> data = {42, 32, 33, 52, 37, 47, 51};
    TrackedArray arr(data);
    bucket_sort(arr);
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
    
    return [42, 32, 33, 52, 37, 47, 51]

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
    """Execute bucket sort"""
    user_code = params.get("code", CODE_SAMPLE)
    test_array = extract_array(user_code)
    function_code = extract_function(user_code)
    
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name="bucket_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
