"""Binary heap operations module - REAL CODE EXECUTION"""

OPERATIONS = [
    {"id": "insert", "name": "Insert Element"},
    {"id": "extract", "name": "Extract Min"},
    {"id": "heapify", "name": "Heapify Array"},
]

CODE_SAMPLES = {
    "insert": """def insert_into_heap(heap, value):
    # Insert value into min heap
    heap.insert(value)
    return heap""",
    
    "extract": """def extract_min(heap):
    # Extract minimum value from heap
    return heap.extract_min()""",
    
    "heapify": """def heapify_array(heap):
    # Convert array to valid heap
    heap.heapify()
    return heap""",
}

def execute(operation, params):
    """Execute USER'S ACTUAL CODE - not presets!"""
    
    # Get user's code if provided, otherwise use default
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Get initial heap values
    initial_values = params.get("values", [5, 3, 8, 1, 9, 2])
    
    # Get operation-specific parameters
    if operation == "insert":
        value = params.get("value", 4)
        return execute_custom_code(user_code, initial_values, "insert_into_heap", [value])
    elif operation == "extract":
        return execute_custom_code(user_code, initial_values, "extract_min", [])
    elif operation == "heapify":
        return execute_custom_code(user_code, initial_values, "heapify_array", [])
    
    return []


def execute_custom_code(code, values, expected_func, extra_params=[]):
    """Execute user's code with TrackedHeap"""
    trace = []
    
    # Create a TrackedHeap
    tracked = TrackedHeap(values, trace)
    
    try:
        # Create execution namespace
        namespace = {
            '__builtins__': __builtins__,
            'print': print,
        }
        
        # Execute user's code
        exec(code, namespace)
        
        # Check if expected function exists
        if expected_func not in namespace:
            raise ValueError(f"Code must define a '{expected_func}' function")
        
        func = namespace[expected_func]
        
        # Execute user's function
        if extra_params:
            result = func(tracked, *extra_params)
        else:
            result = func(tracked)
        
        # Final state
        trace.append({
            "data": tracked.heap.copy(),
            "highlights": [],
            "action": "Operation complete"
        })
        
        return trace
        
    except SyntaxError as e:
        raise ValueError(f"Syntax Error on line {e.lineno}: {e.msg}")
    except Exception as e:
        raise ValueError(f"Runtime Error: {str(e)}")


class TrackedHeap:
    """Min heap wrapper that tracks all operations"""
    def __init__(self, values, trace):
        self.heap = []
        self.trace = trace
        
        # Build initial heap silently
        for val in values:
            self.heap.append(val)
        
        # Record initial state
        self._record_state("Initial array (not yet heapified)")
    
    def insert(self, value):
        """Insert value and maintain heap property"""
        self.heap.append(value)
        self._record_state(f"Added {value} to end", [len(self.heap)-1])
        self._bubble_up(len(self.heap) - 1)
    
    def extract_min(self):
        """Extract minimum value (root)"""
        if not self.heap:
            self._record_state("Cannot extract: heap is empty")
            return None
        
        min_val = self.heap[0]
        self._record_state(f"Extracting min: {min_val}", [0])
        
        # Move last element to root
        self.heap[0] = self.heap[-1]
        self.heap.pop()
        self._record_state("Moved last element to root", [0] if self.heap else [])
        
        # Bubble down if heap not empty
        if self.heap:
            self._bubble_down(0)
        
        return min_val
    
    def heapify(self):
        """Convert array to valid min heap"""
        self._record_state("Starting heapify...")
        # Start from last parent node
        for i in range(len(self.heap) // 2 - 1, -1, -1):
            self._bubble_down(i)
        self._record_state("Heapify complete")
    
    def _bubble_up(self, index):
        """Bubble element up to maintain heap property"""
        if index == 0:
            return
        
        parent = (index - 1) // 2
        if self.heap[index] < self.heap[parent]:
            self.heap[index], self.heap[parent] = self.heap[parent], self.heap[index]
            self._record_state(f"Bubbled up from {index} to {parent}", [parent, index])
            self._bubble_up(parent)
    
    def _bubble_down(self, index):
        """Bubble element down to maintain heap property"""
        smallest = index
        left = 2 * index + 1
        right = 2 * index + 2
        
        if left < len(self.heap) and self.heap[left] < self.heap[smallest]:
            smallest = left
        if right < len(self.heap) and self.heap[right] < self.heap[smallest]:
            smallest = right
        
        if smallest != index:
            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            self._record_state(f"Bubbled down from {index} to {smallest}", [index, smallest])
            self._bubble_down(smallest)
    
    def _record_state(self, action, highlights=[]):
        """Record current state"""
        self.trace.append({
            "data": self.heap.copy(),
            "highlights": highlights,
            "action": action
        })
    
    def __repr__(self):
        return f"Heap({self.heap})"
