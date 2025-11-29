"""Test script for executor"""
from executor import run_bubble_sort

array = [5, 2, 8, 1, 9]
trace = run_bubble_sort(array)
print(f"✓ Generated {len(trace)} trace frames")
print(f"✓ First frame: {trace[0]}")
print(f"✓ Last frame: {trace[-1]}")
print(f"✓ Final array: {trace[-1]['array']}")
assert trace[-1]['array'] == [1, 2, 5, 8, 9], "Array should be sorted"
print("✓ All executor tests passed!")
