"""
Algorithm Executor - Generates step-by-step trace for sorting algorithms
"""
from typing import List, Dict, Any


def run_bubble_sort(array: List[int]) -> List[Dict[str, Any]]:
    """
    Execute bubble sort and generate trace frames for visualization.
    
    Args:
        array: List of integers to sort
        
    Returns:
        List of trace frames, each containing step state
    """
    trace = []
    arr = array.copy()  # Don't modify original
    n = len(arr)
    
    comparisons = 0
    swaps = 0
    step_index = 0
    
    # Initial state frame
    trace.append({
        "stepIndex": step_index,
        "algorithm": "bubble_sort",
        "array": arr.copy(),
        "pointers": {"i": 0, "j": 0},
        "swapOccurred": False,
        "action": "compare",
        "metrics": {"comparisons": comparisons, "swaps": swaps}
    })
    step_index += 1
    
    # Bubble sort algorithm with trace generation
    for i in range(n):
        for j in range(0, n - i - 1):
            # Compare operation
            comparisons += 1
            
            if arr[j] > arr[j + 1]:
                # Swap needed
                trace.append({
                    "stepIndex": step_index,
                    "algorithm": "bubble_sort",
                    "array": arr.copy(),
                    "pointers": {"i": i, "j": j},
                    "swapOccurred": False,
                    "action": "compare",
                    "metrics": {"comparisons": comparisons, "swaps": swaps}
                })
                step_index += 1
                
                # Perform swap
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swaps += 1
                
                trace.append({
                    "stepIndex": step_index,
                    "algorithm": "bubble_sort",
                    "array": arr.copy(),
                    "pointers": {"i": i, "j": j},
                    "swapOccurred": True,
                    "action": "swap",
                    "metrics": {"comparisons": comparisons, "swaps": swaps}
                })
                step_index += 1
            else:
                # No swap needed
                trace.append({
                    "stepIndex": step_index,
                    "algorithm": "bubble_sort",
                    "array": arr.copy(),
                    "pointers": {"i": i, "j": j},
                    "swapOccurred": False,
                    "action": "compare",
                    "metrics": {"comparisons": comparisons, "swaps": swaps}
                })
                step_index += 1
    
    # Final "done" frame
    trace.append({
        "stepIndex": step_index,
        "algorithm": "bubble_sort",
        "array": arr.copy(),
        "pointers": {},
        "swapOccurred": False,
        "action": "done",
        "metrics": {"comparisons": comparisons, "swaps": swaps}
    })
    
    return trace


# For future: other sorting algorithms
def run_insertion_sort(array: List[int]) -> List[Dict[str, Any]]:
    """Insertion sort with trace generation (TODO)"""
    raise NotImplementedError("Insertion sort not yet implemented")


def run_selection_sort(array: List[int]) -> List[Dict[str, Any]]:
    """Selection sort with trace generation (TODO)"""
    raise NotImplementedError("Selection sort not yet implemented")


def run_merge_sort(array: List[int]) -> List[Dict[str, Any]]:
    """Merge sort with trace generation (TODO)"""
    raise NotImplementedError("Merge sort not yet implemented")


def run_quick_sort(array: List[int]) -> List[Dict[str, Any]]:
    """Quick sort with trace generation (TODO)"""
    raise NotImplementedError("Quick sort not yet implemented")
