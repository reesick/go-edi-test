"""
AlgoVisual Backend - Enhanced with output capture and validation
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from modules import array, sorting, bitmask, linkedlist, binaryheap
import sys
from io import StringIO
import time

app = FastAPI(title="AlgoVisual API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Module metadata
MODULES = {
    "array": {
        "name": "Array",
        "operations": array.OPERATIONS,
        "code": array.CODE_SAMPLES
    },
    "sorting": {
        "name": "Sorting",
        "operations": sorting.OPERATIONS,
        "code": sorting.CODE_SAMPLES
    },
    "bitmask": {
        "name": "Bitmask",
        "operations": bitmask.OPERATIONS,
        "code": bitmask.CODE_SAMPLES
    },
    "linkedlist": {
        "name": "Linked List",
        "operations": linkedlist.OPERATIONS,
        "code": linkedlist.CODE_SAMPLES
    },
    "binaryheap": {
        "name": "Binary Heap",
        "operations": binaryheap.OPERATIONS,
        "code": binaryheap.CODE_SAMPLES
    }
}

@app.get("/")
async def root():
    return {"message": "AlgoVisual API", "modules": list(MODULES.keys())}

@app.get("/api/module/{module_name}")
async def get_module(module_name: str):
    """Get module metadata and operations"""
    if module_name not in MODULES:
        return {"error": "Module not found"}
    return MODULES[module_name]

@app.post("/api/validate")
async def validate_code(request: dict):
    """Validate Python syntax"""
    code = request.get("code", "")
    
    try:
        compile(code, '<string>', 'exec')
        return {"valid": True}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": str(e),
            "line": e.lineno,
            "offset": e.offset
        }

@app.post("/api/execute")
async def execute(request: dict):
    """Execute algorithm and return trace with output"""
    module = request.get("module")
    operation = request.get("operation")
    params = request.get("params", {})
    
    if module not in MODULES:
        return {"error": "Module not found"}
    
    # Capture stdout/stderr
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    
    start_time = time.time()
    
    try:
        # Execute the operation
        if module == "array":
            trace = array.execute(operation, params)
        elif module == "sorting":
            trace = sorting.execute(operation, params)
        elif module == "bitmask":
            trace = bitmask.execute(operation, params)
        elif module == "linkedlist":
            trace = linkedlist.execute(operation, params)
        elif module == "binaryheap":
            trace = binaryheap.execute(operation, params)
        else:
            return {"error": "Module not implemented"}
        
        execution_time = time.time() - start_time
        
        # Get captured output
        stdout_value = sys.stdout.getvalue()
        stderr_value = sys.stderr.getvalue()
        
        return {
            "trace": trace,
            "output": {
                "stdout": stdout_value if stdout_value else None,
                "stderr": stderr_value if stderr_value else None,
                "execution_time": execution_time
            }
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Restore stdout/stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
