"""
Debug script to test compilation directly
"""

import asyncio
import sys
sys.path.append('c:\\Users\\ASUS\\Desktop\\bkx\\backend-python')

from algorithms.custom.executor import compile_code, validate_code_safety, validate_code_structure

# Default code from frontend
code = """#include <iostream>
#include <vector>
using namespace std;

int main() {
    // Example: Bubble Sort
    vector<int> arr = {5, 2, 8, 1, 9};
    int n = arr.size();
    
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                swap(arr[j], arr[j+1]);
            }
       }
    }
    
    // Print sorted array
    for (int x : arr) {
        cout << x << " ";
    }
    
    return 0;
}"""

async def main():
    print("=== Testing Code Compilation ===\n")
    
    # Test validation
    print("1. Safety validation...")
    is_safe, error = validate_code_safety(code)
    print(f"   Safe: {is_safe}, Error: {error}")
    
    print("\n2. Structure validation...")
    is_valid, error = validate_code_structure(code)
    print(f"   Valid: {is_valid}, Error: {error}")
    
    # Test compilation
    print("\n3. Compiling...")
    result = await compile_code(code)
    print(f"   Success: {result.success}")
    print(f"   Errors: '{result.errors}'")
    print(f"   Warnings: '{result.warnings}'")
    print(f"   Executable: {result.executable_path}")
    print(f"   Time: {result.compile_time_ms}ms")

if __name__ == "__main__":
    asyncio.run(main())
