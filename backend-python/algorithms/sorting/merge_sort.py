"""Sorting algorithms - Merge Sort"""
from core import cpp_compiler
import re

CODE_SAMPLE = """#include <bits/stdc++.h>
using namespace std;

void merge(TrackedArray& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    
    vector<int> L(n1), R(n2);
    
    for (int i = 0; i < n1; i++)
        L[i] = arr.get(left + i);
    for (int j = 0; j < n2; j++)
        R[j] = arr.get(mid + 1 + j);
    
    int i = 0, j = 0, k = left;
    
    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr.set(k, L[i]);
            i++;
        } else {
            arr.set(k, R[j]);
            j++;
        }
        k++;
    }
    
    while (i < n1) {
        arr.set(k, L[i]);
        i++;
        k++;
    }
    
    while (j < n2) {
        arr.set(k, R[j]);
        j++;
        k++;
    }
}

void merge_sort_helper(TrackedArray& arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;
        merge_sort_helper(arr, left, mid);
        merge_sort_helper(arr, mid + 1, right);
        merge(arr, left, mid, right);
    }
}

void merge_sort(TrackedArray& arr) {
    merge_sort_helper(arr, 0, arr.size() - 1);
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    merge_sort(arr);
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
        function_name="merge_sort",
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
