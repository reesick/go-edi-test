"""
Custom Code Executor - Safely execute user-written Python code
Includes syntax validation, sandboxing, and trace generation
"""
import ast
import sys
import io
import traceback
from typing import Dict, List, Any, Tuple
from contextlib import redirect_stdout, redirect_stderr


def validate_syntax(code: str) -> Tuple[bool, str]:
    """
    Validate Python syntax before execution
    Returns: (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax Error on line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Parse Error: {str(e)}"


def check_forbidden_operations(code: str) -> Tuple[bool, str]:
    """
    Check for forbidden operations (file I/O, network, system calls, etc.)
    Returns: (is_safe, error_message)
    """
    forbidden_modules = ['os', 'sys', 'subprocess', 'socket', 'requests', 'urllib', 'shutil']
    forbidden_functions = ['eval', 'exec', 'compile', '__import__', 'open', 'input']
    
    try:
        tree = ast.parse(code)
        
        for node in ast.walk(tree):
            # Check for forbidden imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_modules:
                        return False, f"Forbidden module: {alias.name}"
            
            if isinstance(node, ast.ImportFrom):
                if node.module in forbidden_modules:
                    return False, f"Forbidden module: {node.module}"
            
            # Check for forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in forbidden_functions:
                        return False, f"Forbidden function: {node.func.id}"
        
        return True, ""
    except Exception as e:
        return False, f"Security check failed: {str(e)}"


def execute_custom_code(code: str, input_data: List[int], timeout: int = 5) -> Dict[str, Any]:
    """
    Execute user's custom sorting code and generate trace
    
    Args:
        code: User's Python code as string
        input_data: Array to sort
        timeout: Execution timeout in seconds
    
    Returns:
        Dict with trace, output, errors, etc.
    """
    # Step 1: Validate syntax
    is_valid, syntax_error = validate_syntax(code)
    if not is_valid:
        return {
            "success": False,
            "error": syntax_error,
            "error_type": "SyntaxError",
            "trace": [],
            "output": ""
        }
    
    # Step 2: Security check
    is_safe, security_error = check_forbidden_operations(code)
    if not is_safe:
        return {
            "success": False,
            "error": security_error,
            "error_type": "SecurityError",
            "trace": [],
            "output": ""
        }
    
    # Step 3: Prepare execution environment
    trace_log = []
    original_array = input_data.copy()
    
    # Create instrumented array class that tracks changes
    class TrackedArray(list):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            trace_log.append({
                "stepIndex": 0,
                "action": "initialized",
                "array": list(self),
                "pointers": {},
                "swapOccurred": False
            })
        
        def __setitem__(self, index, value):
            old_value = self[index] if index < len(self) else None
            super().__setitem__(index, value)
            trace_log.append({
                "stepIndex": len(trace_log),
                "action": f"set arr[{index}] = {value} (was {old_value})",
                "array": list(self),
                "pointers": {"modified": index},
                "swapOccurred": False
            })
    
    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        # Create safe execution namespace
        safe_globals = {
            '__builtins__': {
                'range': range,
                'len': len,
                'print': print,
                'sorted': sorted,
                'min': min,
                'max': max,
                'sum': sum,
                'abs': abs,
                'int': int,
                'float': float,
                'str': str,
                'list': list,
                'tuple': tuple,
                'dict': dict,
                'set': set,
                'True': True,
                'False': False,
                'None': None
            }
        }
        
        # Execute code with redirected output
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Compile and execute
            compiled_code = compile(code, '<user_code>', 'exec')
            exec(compiled_code, safe_globals)
            
            # Look for main algorithm function
            # Common names: sort, bubble_sort, sorting_algorithm, main
            func_names = ['sort', 'bubble_sort', 'insertion_sort', 'selection_sort', 
                         'quick_sort', 'merge_sort', 'sorting_algorithm', 'main']
            
            sort_func = None
            for name in func_names:
                if name in safe_globals and callable(safe_globals[name]):
                    sort_func = safe_globals[name]
                    break
            
            if not sort_func:
                # Try to find any function that takes a list
                for name, obj in safe_globals.items():
                    if callable(obj) and not name.startswith('__'):
                        sort_func = obj
                        break
            
            if not sort_func:
                return {
                    "success": False,
                    "error": "No sorting function found. Define a function like: def sort(arr):",
                    "error_type": "FunctionNotFoundError",
                    "trace": [],
                    "output": stdout_capture.getvalue()
                }
            
            # Execute the sorting function with tracked array
            tracked_arr = TrackedArray(original_array)
            result = sort_func(tracked_arr)
            
            # If function returns array, use that
            if result is not None:
                final_array = list(result)
            else:
                final_array = list(tracked_arr)
            
            # Add final state
            trace_log.append({
                "stepIndex": len(trace_log),
                "action": "completed",
                "array": final_array,
                "pointers": {},
                "swapOccurred": False
            })
        
        return {
            "success": True,
            "trace": trace_log,
            "output": stdout_capture.getvalue(),
            "error": "",
            "final_array": final_array,
            "is_sorted": final_array == sorted(original_array),
            "steps": len(trace_log)
        }
        
    except Exception as e:
        error_trace = traceback.format_exc()
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__,
            "error_trace": error_trace,
            "trace": trace_log,  # Return partial trace
            "output": stdout_capture.getvalue()
        }


def analyze_algorithm_complexity(trace: List[Dict]) -> Dict[str, Any]:
    """
    Analyze the complexity of the algorithm from its trace
    """
    comparisons = 0
    swaps = 0
    array_accesses = 0
    
    for step in trace:
        action = step.get("action", "")
        if "comparing" in action.lower():
            comparisons += 1
        if "swap" in action.lower():
            swaps += 1
        if "arr[" in action:
            array_accesses += 1
    
    n = len(trace[0]["array"]) if trace else 0
    
    # Rough complexity estimation
    if comparisons > n * (n - 1) / 2:
        time_complexity = "O(n²) or worse"
    elif comparisons > n * (n - 1) / 4:
        time_complexity = "~O(n²)"
    elif comparisons > n:
        time_complexity = "~O(n log n)"
    else:
        time_complexity = "O(n)"
    
    return {
        "comparisons": comparisons,
        "swaps": swaps,
        "array_accesses": array_accesses,
        "estimated_time_complexity": time_complexity,
        "total_steps": len(trace)
    }
