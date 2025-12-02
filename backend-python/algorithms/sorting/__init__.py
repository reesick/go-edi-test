"""Sorting algorithms module"""
from . import bubble_sort, selection_sort, insertion_sort, merge_sort, quick_sort, heap_sort, shell_sort
from . import counting_sort, radix_sort, bucket_sort

OPERATIONS = [
    {"id": "bubble", "name": "Bubble Sort"},
    {"id": "selection", "name": "Selection Sort"},
    {"id": "insertion", "name": "Insertion Sort"},
    {"id": "merge", "name": "Merge Sort"},
    {"id": "quick", "name": "Quick Sort"},
    {"id": "heap", "name": "Heap Sort"},
    {"id": "shell", "name": "Shell Sort"},
    {"id": "counting", "name": "Counting Sort"},
    {"id": "radix", "name": "Radix Sort"},
    {"id": "bucket", "name": "Bucket Sort"},
]

CODE_SAMPLES = {
    "bubble": bubble_sort.CODE_SAMPLE,
    "selection": selection_sort.CODE_SAMPLE,
    "insertion": insertion_sort.CODE_SAMPLE,
    "merge": merge_sort.CODE_SAMPLE,
    "quick": quick_sort.CODE_SAMPLE,
    "heap": heap_sort.CODE_SAMPLE,
    "shell": shell_sort.CODE_SAMPLE,
    "counting": counting_sort.CODE_SAMPLE,
    "radix": radix_sort.CODE_SAMPLE,
    "bucket": bucket_sort.CODE_SAMPLE,
}

def execute(operation, params):
    """Execute sorting algorithm"""
    executors = {
        "bubble": bubble_sort.execute,
        "selection": selection_sort.execute,
        "insertion": insertion_sort.execute,
        "merge": merge_sort.execute,
        "quick": quick_sort.execute,
        "heap": heap_sort.execute,
        "shell": shell_sort.execute,
        "counting": counting_sort.execute,
        "radix": radix_sort.execute,
        "bucket": bucket_sort.execute,
    }
    
    executor = executors.get(operation)
    if not executor:
        raise ValueError(f"Unknown sorting operation: {operation}")
    
    return executor(params)
