"""Searching algorithms package"""
from .linear_search import execute as linear_execute, CODE_SAMPLE as linear_sample
from .sentinel_search import execute as sentinel_execute, CODE_SAMPLE as sentinel_sample
from .fibonacci_search import execute as fibonacci_execute, CODE_SAMPLE as fibonacci_sample
from .indexed_sequential_search import execute as indexed_execute, CODE_SAMPLE as indexed_sample

OPERATIONS = [
    {"id": "linear", "name": "Linear Search"},
    {"id": "sentinel", "name": "Sentinel Search"},
    {"id": "fibonacci", "name": "Fibonacci Search"},
    {"id": "indexed", "name": "Indexed Sequential Search"},
]

CODE_SAMPLES = {
    "linear": linear_sample,
    "sentinel": sentinel_sample,
    "fibonacci": fibonacci_sample,
    "indexed": indexed_sample,
}

def execute(operation, params):
    """Route to specific search algorithm"""
    if operation == "linear":
        return linear_execute(params)
    elif operation == "sentinel":
        return sentinel_execute(params)
    elif operation == "fibonacci":
        return fibonacci_execute(params)
    elif operation == "indexed":
        return indexed_execute(params)
    
    raise ValueError(f"Unknown operation: {operation}")
