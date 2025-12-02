"""Sorting module - C++ code execution with FULL programs and LINE TRACKING"""
from cpp_compiler import cpp_compiler
from cpp_compiler.instrumenter import extract_function_code
import re

OPERATIONS = [
    {"id": "bubble", "name": "Bubble Sort"},
    {"id": "selection", "name": "Selection Sort"},
    {"id": "insertion", "name": "Insertion Sort"},
]

CODE_SAMPLES = {
    "bubble": """#include <bits/stdc++.h>
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
}""",
    
    "selection": """#include <bits/stdc++.h>
using namespace std;

void selection_sort(TrackedArray& arr) {
    int n = arr.size();
    for (int i = 0; i < n-1; i++) {
        int min_idx = i;
        for (int j = i+1; j < n; j++) {
            if (arr.get(j) < arr.get(min_idx)) {
                min_idx = j;
            }
        }
        if (min_idx != i) {
            arr.swap(i, min_idx);
        }
    }
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    selection_sort(arr);
    arr.print_trace();
    return 0;
}""",
    
    "insertion": """#include <bits/stdc++.h>
using namespace std;

void insertion_sort(TrackedArray& arr) {
    int n = arr.size();
    for (int i = 1; i < n; i++) {
        int key = arr.get(i);
        int j = i - 1;
        while (j >= 0 && arr.get(j) > key) {
            arr.set(j+1, arr.get(j));
            j--;
        }
        arr.set(j+1, key);
    }
}

int main() {
    vector<int> data = {5, 2, 8, 1, 9, 3};
    TrackedArray arr(data);
    insertion_sort(arr);
    arr.print_trace();
    return 0;
}"""
}

def extract_array_from_code(code):
    """Extract array/vector values from user's C++ code"""
    patterns = [
        r'vector<int>\s+\w+\s*=\s*\{([^}]+)\}',
        r'vector<int>\s+\w+\s*\{([^}]+)\}',
        r'int\s+\w+\[\]\s*=\s*\{([^}]+)\}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, code)
        if match:
            numbers_str = match.group(1)
            numbers = [int(x.strip()) for x in numbers_str.split(',') if x.strip().isdigit() or (x.strip().lstrip('-').isdigit())]
            if numbers:
                return numbers
    
    return [5, 2, 8, 1, 9, 3]

def execute(operation, params):
    """Execute user's C++ code with LINE-BY-LINE tracking"""
    
    # Get user's code
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Extract user's array
    test_array = extract_array_from_code(user_code)
    
    # Extract function code (skip headers/main)
    function_code = extract_function_code(user_code)
    
    # Function name
    function_map = {
        "bubble": "bubble_sort",
        "selection": "selection_sort",
        "insertion": "insertion_sort"
    }
    function_name = function_map.get(operation, "bubble_sort")
    
    # Compile with line tracking
    result = cpp_compiler.compile_and_execute(
        user_code=function_code,
        module_type="sorting",
        function_name=function_name,
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
