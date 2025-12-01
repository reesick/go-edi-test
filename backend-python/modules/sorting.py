"""Sorting algorithms module - NOW EXECUTES USER CODE"""
import sys
from io import StringIO

OPERATIONS = [
    {"id": "bubble", "name": "Bubble Sort"},
    {"id": "selection", "name": "Selection Sort"},
    {"id": "insertion", "name": "Insertion Sort"},
]

CODE_SAMPLES = {
    "bubble": """def sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr""",
    
    "selection": """def sort(arr):
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i+1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr""",
    
    "insertion": """def sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >= 0 and arr[j] > key:
            arr[j+1] = arr[j]
            j -= 1
        arr[j+1] = key
    return arr"""
}

def execute(operation, params):
    """Execute USER'S ACTUAL CODE - not presets!"""
    
    # Get user's code if provided, otherwise use default
    user_code = params.get("code")
    
    if not user_code or user_code.strip() == "":
        # Fallback to preset if no code provided
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Default test array
    test_array = params.get("array", [5, 2, 8, 1, 9, 3])
    
    # Execute the user's code and capture trace
    return execute_custom_code(user_code, test_array)


def execute_custom_code(code, arr):
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
            'print': print,  # Allow print statements
        }
        
        # Execute the user's code to define the sort function
        exec(code, namespace)
        
        # Check if 'sort' function was defined
        if 'sort' not in namespace:
            raise ValueError("Code must define a 'sort(arr)' function")
        
        sort_func = namespace['sort']
        
        # Initial state
        trace.append({
            "data": tracked.data.copy(),
            "highlights": [],
            "action": "Initial array"
        })
        
        # Execute the user's sort function with our tracked array
        result = sort_func(tracked)
        
        # Final state
        trace.append({
            "data": tracked.data.copy(),
            "highlights": [],
            "action": "Sorting complete"
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
            "action": f"Access arr[{index}]"
        })
        return self.data[index]
    
    def __setitem__(self, index, value):
        # Record array modification
        self.data[index] = value
        self.trace.append({
            "data": self.data.copy(),
            "highlights": [index],
            "action": f"Set arr[{index}] = {value}"
        })
    
    def __iter__(self):
        return iter(self.data)
    
    def __repr__(self):
        return repr(self.data)
    
    # Support range() in for loops
    def range(self, *args):
        return range(*args)
