"""
Custom Code Execution Routes
Separate module to keep main.py clean
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import custom_executor

router = APIRouter()


class ExecuteCustomCodeRequest(BaseModel):
    code: str
    array: List[int]


@router.post("/execute-custom")
async def execute_custom_code_endpoint(request: ExecuteCustomCodeRequest):
    """Execute user's custom Python code with validation and sandboxing"""
    try:
        if not request.array:
            raise HTTPException(status_code=400, detail="Array cannot be empty")
        
        if not request.code.strip():
            raise HTTPException(status_code=400, detail="Code cannot be empty")
        
        result = custom_executor.execute_custom_code(request.code, request.array)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "errorType": result.get("error_type", "Unknown"),
                "trace": result.get("trace", []),
                "output": result.get("output", "")
            }
        
        complexity = custom_executor.analyze_algorithm_complexity(result["trace"]) if result["trace"] else {}
        
        return {
            "success": True,
            "trace": result["trace"],
            "output": result["output"],
            "finalArray": result.get("final_array", []),
            "isSorted": result.get("is_sorted", False),
            "complexity": complexity
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
