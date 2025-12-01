"""Bitmask operations module - REAL CODE EXECUTION"""

OPERATIONS = [
    {"id": "set", "name": "Set Bit"},
    {"id": "clear", "name": "Clear Bit"},
    {"id": "toggle", "name": "Toggle Bit"},
    {"id": "check", "name": "Check Bit"},
    {"id": "count", "name": "Count Set Bits"},
]

CODE_SAMPLES = {
    "set": """def set_bit(bitmask, position):
    # Set bit at position to 1
    bitmask.set_bit(position)
    return bitmask""",
    
    "clear": """def clear_bit(bitmask, position):
    # Clear bit at position to 0
    bitmask.clear_bit(position)
    return bitmask""",
    
    "toggle": """def toggle_bit(bitmask, position):
    # Toggle bit at position
    bitmask.toggle_bit(position)
    return bitmask""",
    
    "check": """def check_bit(bitmask, position):
    # Check if bit at position is set
    return bitmask.check_bit(position)""",
    
    "count": """def count_bits(bitmask):
    # Count number of set bits
    return bitmask.count_set_bits()"""
}

def execute(operation, params):
    """Execute USER'S ACTUAL CODE - not presets!"""
    
    # Get user's code if provided, otherwise use default
    user_code = params.get("code")
    if not user_code or user_code.strip() == "":
        user_code = CODE_SAMPLES.get(operation, "")
    
    # Get initial bitmask value
    initial_value = params.get("value", 10)  # Default: 1010 in binary
    
    # Get operation-specific parameters
    if operation in ["set", "clear", "toggle", "check"]:
        position = params.get("position", 2)
        expected_func = f"{operation}_bit"
        return execute_custom_code(user_code, initial_value, expected_func, [position])
    elif operation == "count":
        return execute_custom_code(user_code, initial_value, "count_bits", [])
    
    return []


def execute_custom_code(code, value, expected_func, extra_params=[]):
    """Execute user's code with TrackedBitmask"""
    trace = []
    
    # Create a TrackedBitmask
    tracked = TrackedBitmask(value, trace)
    
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
        
        # Initial state
        trace.append({
            "data": tracked.value,
            "highlights": [],
            "action": f"Initial value: {tracked.value} ({bin(tracked.value)})"
        })
        
        # Execute user's function
        if extra_params:
            result = func(tracked, *extra_params)
        else:
            result = func(tracked)
        
        # Final state
        trace.append({
            "data": tracked.value,
            "highlights": [],
            "action": f"Final value: {tracked.value} ({bin(tracked.value)})"
        })
        
        return trace
        
    except SyntaxError as e:
        raise ValueError(f"Syntax Error on line {e.lineno}: {e.msg}")
    except Exception as e:
        raise ValueError(f"Runtime Error: {str(e)}")


class TrackedBitmask:
    """Bitmask wrapper that tracks all bit operations"""
    def __init__(self, value, trace):
        self.value = value
        self.trace = trace
    
    def set_bit(self, pos):
        """Set bit at position to 1"""
        old_value = self.value
        self.value |= (1 << pos)
        self.trace.append({
            "data": self.value,
            "highlights": [pos],
            "action": f"Set bit {pos}: {bin(old_value)} → {bin(self.value)}"
        })
    
    def clear_bit(self, pos):
        """Clear bit at position to 0"""
        old_value = self.value
        self.value &= ~(1 << pos)
        self.trace.append({
            "data": self.value,
            "highlights": [pos],
            "action": f"Clear bit {pos}: {bin(old_value)} → {bin(self.value)}"
        })
    
    def toggle_bit(self, pos):
        """Toggle bit at position"""
        old_value = self.value
        self.value ^= (1 << pos)
        self.trace.append({
            "data": self.value,
            "highlights": [pos],
            "action": f"Toggle bit {pos}: {bin(old_value)} → {bin(self.value)}"
        })
    
    def check_bit(self, pos):
        """Check if bit at position is set"""
        is_set = (self.value >> pos) & 1
        self.trace.append({
            "data": self.value,
            "highlights": [pos],
            "action": f"Check bit {pos}: {is_set}"
        })
        return is_set
    
    def count_set_bits(self):
        """Count number of 1 bits"""
        count = bin(self.value).count('1')
        self.trace.append({
            "data": self.value,
            "highlights": [],
            "action": f"Count set bits: {count}"
        })
        return count
    
    def __repr__(self):
        return f"Bitmask({self.value}, {bin(self.value)})"
