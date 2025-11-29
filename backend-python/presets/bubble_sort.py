def bubble_sort(arr):
    """
    Standard bubble sort implementation.
    Repeatedly steps through list, compares adjacent elements and swaps them if they are in wrong order.
    """
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
