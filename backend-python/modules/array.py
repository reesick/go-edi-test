"""Array operations module - NOW USES C++ CODE EXECUTION"""
from cpp_compiler import cpp_compiler

OPERATIONS = [
    {"id": "access", "name": "Access by Index"},
    {"id": "insert", "name": "Insert at Index"},
    {"id": "delete", "name": "Delete at Index"},
    {"id": "search", "name": "Linear Search"},
    {"id": "reverse", "name": "Reverse Array"},
]

CODE_SAMPLES = {
    "access": """void access_element(TrackedArray& arr) {
    // Access element at index 2
    int value = arr[2];
}""",
    
    "insert": """void insert_element(TrackedArray& arr) {
    // Insert value 99 at index 2
    arr.insert(2, 99);
}""",
    
    "delete": """void delete_element(TrackedArray& arr) {
    // Delete element at index 1
    arr.erase(1);
}""",
    
    "search": """void search_value(TrackedArray& arr) {
    // Linear search for value 8
    int target = 8;
    for (int i = 0; i < arr.size(); i++) {
        if (arr.get(i) == target) {
            int found = arr[i]; // Mark as found
            break;
        }
    }
}""",
    
    "reverse": """void reverse_array(TrackedArray& arr) {
    // Reverse array in place
    int left = 0, right = arr.size() - 1;
    while (left < right) {
        arr.swap(left, right);
        left++;
        right--;
    }
}"""
}

def execute(operation, params):
    """Execute USER'S C++ CODE via compilation!"""
    
    # Get user's code or use default
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Default test array
    test_array = params.get("array", [5, 2, 8, 1, 9, 3])
    
    # Determine function name
    function_map = {
        "access": "access_element",
        "insert": "insert_element",
        "delete": "delete_element",
        "search": "search_value",
        "reverse": "reverse_array"
    }
    function_name = function_map.get(operation, "access_element")
    
    # Compile and execute C++
    result = cpp_compiler.compile_and_execute(
        user_code=user_code,
        module_type="array",
        function_name=function_name,
        initial_data=test_array
    )
    
    if not result["success"]:
        raise ValueError(result.get("error", "Compilation failed"))
    
    return result.get("trace", [])
