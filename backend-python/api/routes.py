"""API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core import cpp_compiler
import algorithms

router = APIRouter()

class ValidateRequest(BaseModel):
    code: str

class ExecuteRequest(BaseModel):
    module: str
    operation: str
    params: dict

@router.get("/api/modules")
async def list_modules():
    """List all available modules"""
    modules_list = []
    for module_id, module_data in algorithms.MODULES.items():
        modules_list.append({
            "id": module_id,
            "name": module_data["name"],
            "icon": module_data.get("icon", "📦"),
            "count": len(module_data["operations"])
        })
    return {"modules": modules_list}

@router.get("/api/module/{module_name}")
async def get_module(module_name: str):
    """Get module configuration"""
    module = algorithms.get_module(module_name)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module

@router.post("/api/validate")
async def validate_code(request: ValidateRequest):
    """Validate C++ syntax"""
    result = cpp_compiler.validate_syntax(request.code)
    return result

@router.post("/api/execute")
async def execute_code(request: ExecuteRequest):
    """Execute algorithm"""
    try:
        trace = algorithms.execute_module(
            request.module,
            request.operation,
            request.params
        )
        return {"trace": trace, "error": None}
    except Exception as e:
        return {"trace": [], "error": str(e)}
