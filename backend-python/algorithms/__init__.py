"""Algorithms package - organized by category"""

# Import category modules
from .sorting import OPERATIONS as SORTING_OPS, CODE_SAMPLES as SORTING_SAMPLES, execute as sorting_execute
from .searching import OPERATIONS as SEARCHING_OPS, CODE_SAMPLES as SEARCHING_SAMPLES, execute as searching_execute

# Module registry
MODULES = {
    "sorting": {
        "name": "Sorting Algorithms",
        "icon": "↕️",
        "operations": SORTING_OPS,
        "code": SORTING_SAMPLES,
        "execute": sorting_execute,
    },
    "searching": {
        "name": "Searching Algorithms",
        "icon": "🔍",
        "operations": SEARCHING_OPS,
        "code": SEARCHING_SAMPLES,
        "execute": searching_execute,
    },
}

def get_module(module_name):
    """Get module configuration"""
    return MODULES.get(module_name)

def execute_module(module_name, operation, params):
    """Execute algorithm"""
    module = MODULES.get(module_name)
    if not module:
        raise ValueError(f"Module not found: {module_name}")
    
    return module["execute"](operation, params)
