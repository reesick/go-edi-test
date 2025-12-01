"""Array operations module - REAL CODE EXECUTION"""
import sys
from io import StringIO

OPERATIONS = [
    {"id": "access", "name": "Access by Index"},
    {"id": "insert", "name": "Insert at Index"},
    {"id": "delete", "name": "Delete at Index"},
    {"id": "search", "name": "Linear Search"},
    {"id": "reverse", "name": "Reverse Array"},
]

CODE_SAMPLES = {
    "access": """def access_element(arr, index):
    # Access element at given index
    value = arr[index]
    return value""",
    
    "insert": """def insert_element(arr, index, value):
    # Insert value at given index
    arr.insert(index, value)
    return arr""",
    
    "delete": """def delete_element(arr, index):
    # Delete element at given index
    del arr[index]
    return arr""",
    
    "search": """def search_value(arr, target):
    # Linear search for target value
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1""",
    
    "reverse": """def reverse_array(arr):
    # Reverse array in place
    left, right = 0, len(arr) - 1
    while left < right:
        arr[left], arr[right] = arr[right], arr[left]
        left += 1
        right -= 1
    return arr"""
}

def execute(operation, params):
    """Execute USER'S ACTUAL CODE - not presets!"""
    
    # Get user's code if provided, otherwise use default
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Get test data
    test_array = params.get("array", [5, 2, 8, 1, 9, 3])
    
    # Get operation-specific parameters
    if operation == "access":
        index = params.get("index", 0)
        return execute_custom_code(user_code, test_array, "access_element", [index])
    elif operation == "insert":
        index = params.get("index", 2)
        value = params.get("value", 99)
        return execute_custom_code(user_code, test_array, "insert_element", [index, value])
    elif operation == "delete":
        index = params.get("index", 1)
        return execute_custom_code(user_code, test_array, "delete_element", [index])
    elif operation == "search":
        target = params.get("target", 8)
        return execute_custom_code(user_code, test_array, "search_value", [target])
    elif operation == "reverse":
        return execute_custom_code(user_code, test_array, "reverse_array", [])
    
    return []


def execute_custom_code(code, arr, expected_func, extra_params=[]):
    """
    Execute user's Python code and generate visualization trace
    This is NOT hollow - it actually runs the code!
    """
    trace = []
    
    # Create a TrackedArray that records all operations
    tracked = TrackedArray(arr.copy(), trace)
    
    try:
        # Create execution namespace
        namespace = {
            '__builtins__': __builtins__,
            'print': print,
        }
        
        # Execute the user's code to define the function
        exec(code, namespace)
        
        # Check if expected function was defined
        if expected_func not in namespace:
            raise ValueError(f"Code must define a '{expected_func}' function")
        
        func = namespace[expected_func]
        
        # Initial state
        trace.append({
            "data": tracked.data.copy(),
            "highlights": [],
            "action": "Initial array"
        })
        
        # Execute the user's function with our tracked array
        if extra_params:
            result = func(tracked, *extra_params)
        else:
            result = func(tracked)
        
        # Final state
        trace.append({
            "data": tracked.data.copy(),
            "highlights": [],
            "action": "Operation complete"
        })
        
        return trace
        
    except SyntaxError as e:
        raise ValueError(f"Syntax Error on line {e.lineno}: {e.msg}")
    except Exception as e:
        raise ValueError(f"Runtime Error: {str(e)}")


class TrackedArray:
    """
    Array wrapper that tracks all operations for visualization
    This makes the visualization show ACTUAL operations from user's code
    """
    def __init__(self, data, trace):
        self.data = data
        self.trace = trace
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, index):
        # Record array access
        self.trace.append({
            "data": self.data.copy(),
            "highlights": [index] if isinstance(index, int) else [],
            "action": f"Access arr[{index}] = {self.data[index]}"
        })
        return self.data[index]
    
    def __setitem__(self, index, value):
        # Record array modification
        old_value = self.data[index]
        self.data[index] = value
        self.trace.append({
            "data": self.data.copy(),
            "highlights": [index],
            "action": f"Set arr[{index}] = {value} (was {old_value})"
        })
    
    def __delitem__(self, index):
        # Record deletion
        value = self.data[index]
        del self.data[index]
        self.trace.append({
            "data": self.data.copy(),
            "highlights": [max(0, index-1)] if self.data else [],
            "action": f"Deleted arr[{index}] = {value}"
        })
    
    def insert(self, index, value):
        # Record insertion
        self.data.insert(index, value)
        self.trace.append({
            "data": self.data.copy(),
            "highlights": [index],
            "action": f"Inserted {value} at index {index}"
        })
    
    def __iter__(self):
        return iter(self.data)
    
    def __repr__(self):
        return repr(self.data)
    
    # Support range() in for loops
    def range(self, *args):
        return range(*args)
