"""Linked list operations module - REAL CODE EXECUTION"""

OPERATIONS = [
    {"id": "insert_head", "name": "Insert at Head"},
    {"id": "insert_tail", "name": "Insert at Tail"},
    {"id": "delete", "name": "Delete Node"},
    {"id": "search", "name": "Search Value"},
    {"id": "reverse", "name": "Reverse List"},
]

CODE_SAMPLES = {
    "insert_head": """def insert_at_head(linked_list, value):
    # Insert value at the head of the list
    linked_list.insert_head(value)
    return linked_list""",
    
    "insert_tail": """def insert_at_tail(linked_list, value):
    # Insert value at the tail of the list
    linked_list.insert_tail(value)
    return linked_list""",
    
    "delete": """def delete_node(linked_list, value):
    # Delete first node with given value
    linked_list.delete(value)
    return linked_list""",
    
    "search": """def search_value(linked_list, value):
    # Search for value in linked list
    return linked_list.search(value)""",
    
    "reverse": """def reverse_list(linked_list):
    # Reverse the linked list
    linked_list.reverse()
    return linked_list"""
}

def execute(operation, params):
    """Execute USER'S ACTUAL CODE - not presets!"""
    
    # Get user's code if provided, otherwise use default
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Get initial list values
    initial_values = params.get("values", [1, 2, 3, 4, 5])
    
    # Get operation-specific parameters
    if operation == "insert_head":
        value = params.get("value", 99)
        return execute_custom_code(user_code, initial_values, "insert_at_head", [value])
    elif operation == "insert_tail":
        value = params.get("value", 99)
        return execute_custom_code(user_code, initial_values, "insert_at_tail", [value])
    elif operation == "delete":
        value = params.get("value", 3)
        return execute_custom_code(user_code, initial_values, "delete_node", [value])
    elif operation == "search":
        value = params.get("value", 4)
        return execute_custom_code(user_code, initial_values, "search_value", [value])
    elif operation == "reverse":
        return execute_custom_code(user_code, initial_values, "reverse_list", [])
    
    return []


def execute_custom_code(code, values, expected_func, extra_params=[]):
    """Execute user's code with TrackedLinkedList"""
    trace = []
    
    # Create a TrackedLinkedList
    tracked = TrackedLinkedList(values, trace)
    
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
            "data": tracked._to_array(),
            "highlights": [],
            "action": "Operation complete"
        })
        
        return trace
        
    except SyntaxError as e:
        raise ValueError(f"Syntax Error on line {e.lineno}: {e.msg}")
    except Exception as e:
        raise ValueError(f"Runtime Error: {str(e)}")


class Node:
    """Simple linked list node"""
    def __init__(self, value):
        self.value = value
        self.next = None


class TrackedLinkedList:
    """Linked list wrapper that tracks all operations"""
    def __init__(self, values, trace):
        self.trace = trace
        self.head = None
        
        # Build initial list silently
        for val in values:
            self._append_silent(val)
        
        # Record initial state
        self._record_state("Initial linked list")
    
    def _append_silent(self, value):
        """Add node without recording"""
        new_node = Node(value)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
    
    def insert_head(self, value):
        """Insert at head with tracking"""
        new_node = Node(value)
        new_node.next = self.head
        self.head = new_node
        self._record_state(f"Inserted {value} at head")
    
    def insert_tail(self, value):
        """Insert at tail with tracking"""
        new_node = Node(value)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self._record_state(f"Inserted {value} at tail")
    
    def delete(self, value):
        """Delete first node with value"""
        if not self.head:
            self._record_state(f"Cannot delete {value}: list is empty")
            return
        
        # If head node
        if self.head.value == value:
            self.head = self.head.next
            self._record_state(f"Deleted {value} from head")
            return
        
        # Search for node
        current = self.head
        while current.next:
            if current.next.value == value:
                current.next = current.next.next
                self._record_state(f"Deleted {value}")
                return
            current = current.next
        
        self._record_state(f"Value {value} not found")
    
    def search(self, value):
        """Search for value"""
        current = self.head
        index = 0
        while current:
            if current.value == value:
                self._record_state(f"Found {value} at index {index}", [index])
                return index
            current = current.next
            index += 1
        self._record_state(f"Value {value} not found")
        return -1
    
    def reverse(self):
        """Reverse the linked list"""
        prev = None
        current = self.head
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
            self._record_state("Reversing...")
        self.head = prev
        self._record_state("Reverse complete")
    
    def _to_array(self):
        """Convert to array for visualization"""
        result = []
        current = self.head
        while current:
            result.append(current.value)
            current = current.next
        return result
    
    def _record_state(self, action, highlights=[]):
        """Record current state"""
        self.trace.append({
            "data": self._to_array(),
            "highlights": highlights,
            "action": action
        })
    
    def __repr__(self):
        return f"LinkedList({self._to_array()})"
