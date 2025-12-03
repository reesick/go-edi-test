"""
Custom Code API Routes

FastAPI routes for custom code compilation, execution, and AI-powered visualization.
Includes rate limiting, error handling, and comprehensive logging.
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
import logging
import time

from algorithms.custom.executor import (
    compile_code,
    execute_code,
   cleanup_temp_files,
    validate_code_safety
)
from ai.custom_linesync.service import (
    generate_visualization_and_linesync,
    health_check
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models

class CompileRequest(BaseModel):
    """Request to compile custom C++ code"""
    code: str = Field(..., min_length=1, max_length=50000)
    
    @validator('code')
    def validate_code_length(cls, v):
        lines = v.splitlines()
        if len(lines) > 100:
            raise ValueError(f'Code exceeds 100 lines (got {len(lines)} lines)')
        return v


class CompileResponse(BaseModel):
    """Response from compilation"""
    success: bool
    executable_path: Optional[str] = None
    errors: str = ""
    warnings: str = ""
    compile_time_ms: int = 0


class VisualizeRequest(BaseModel):
    """Request to generate visualization and linesync"""
    code: str = Field(..., min_length=1, max_length=50000)
    input_data: str = Field(default="", max_length=10000)
    executable_path: Optional[str] = None
    
    @validator('code')
    def validate_code_length(cls, v):
        lines = v.splitlines()
        if len(lines) > 100:
            raise ValueError(f'Code exceeds 100 lines (got {len(lines)} lines)')
        return v


class VisualizeResponse(BaseModel):
    """Response with visualization and linesync data"""
    metadata: Dict[str, Any]
    visualization: Dict[str, Any]
    linesync: Dict[str, Any]
    execution_output: Optional[str] = None
    is_fallback: bool = False


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    detail: Optional[str] = None
    code: str


# Simple in-memory rate limiting (production should use Redis)
rate_limit_store: Dict[str, list] = {}

def check_rate_limit(client_ip: str, max_requests: int, window_seconds: int) -> bool:
    """
    Simple rate limiting check.
    
    Args:
        client_ip: Client IP address
        max_requests: Maximum requests allowed
        window_seconds: Time window in seconds
    
    Returns:
        True if within limit, False if exceeded
    """
    current_time = time.time()
    
    if client_ip not in rate_limit_store:
        rate_limit_store[client_ip] = []
    
    # Remove old requests outside the window
    rate_limit_store[client_ip] = [
        req_time for req_time in rate_limit_store[client_ip]
        if current_time - req_time < window_seconds
    ]
    
    # Check if limit exceeded
    if len(rate_limit_store[client_ip]) >= max_requests:
        return False
    
    # Add current request
    rate_limit_store[client_ip].append(current_time)
    return True


def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# API Endpoints

@router.post("/compile", response_model=CompileResponse)
async def compile_custom_code(request_data: CompileRequest, request: Request):
    """
    Compile user-submitted C++ code.
    
    Rate limit: 20 requests per minute per IP
    """
    client_ip = get_client_ip(request)
    
    # Rate limiting
    if not check_rate_limit(client_ip, max_requests=20, window_seconds=60):
        logger.warning(f"Rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait before trying again."
        )
    
    try:
        # Validate code safety
        is_safe, error_msg = validate_code_safety(request_data.code)
        if not is_safe:
            logger.warning(f"Unsafe code rejected from {client_ip}: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Code validation failed: {error_msg}"
            )
        
        # Compile code
        logger.info(f"Compiling code from {client_ip}")
        result = await compile_code(request_data.code)
        
        if result.success:
            logger.info(f"Compilation successful for {client_ip} in {result.compile_time_ms}ms")
        else:
            logger.warning(f"Compilation failed for {client_ip}: {result.errors[:200]}")
        
        return CompileResponse(
            success=result.success,
            executable_path=result.executable_path,
            errors=result.errors,
            warnings=result.warnings,
            compile_time_ms=result.compile_time_ms
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error during compilation for {client_ip}")
        raise HTTPException(
            status_code=500,
            detail=f"Compilation service error: {str(e)}"
        )


@router.post("/visualize-with-linesync", response_model=VisualizeResponse)
async def generate_visualization(request_data: VisualizeRequest, request: Request):
    """
    Generate visualization and linesync data using Gemini AI.
    
    Rate limit: 10 requests per minute per IP (stricter due to AI cost)
    """
    client_ip = get_client_ip(request)
    
    # Stricter rate limiting for AI calls
    if not check_rate_limit(client_ip, max_requests=10, window_seconds=60):
        logger.warning(f"AI rate limit exceeded for {client_ip}")
        raise HTTPException(
            status_code=429,
            detail="AI rate limit exceeded. Please wait 1 minute before trying again."
        )
    
    execution_output = ""
    
    try:
        # Execute code if executable path provided
        if request_data.executable_path:
            logger.info(f"Executing code from {client_ip}")
            exec_result = await execute_code(
                request_data.executable_path,
                request_data.input_data,
                timeout=10
            )
            
            if exec_result.timed_out:
                raise HTTPException(
                    status_code=408,
                    detail="Code execution timeout (10s limit). Please optimize your code."
                )
            
            execution_output = exec_result.stdout
            
            # Clean up after execution
            cleanup_temp_files(request_data.executable_path)
        
        # Generate visualization with AI
        logger.info(f"Generating visualization for {client_ip}")
        start_time = time.time()
        
        result = await generate_visualization_and_linesync(
            code=request_data.code,
            input_data=request_data.input_data,
            execution_output=execution_output
        )
        
        ai_time = int((time.time() - start_time) * 1000)
        logger.info(f"Visualization generated for {client_ip} in {ai_time}ms")
        
        # Check if fallback was used
        is_fallback = result.get('metadata', {}).get('is_fallback', False)
        if is_fallback:
            logger.warning(f"Fallback visualization used for {client_ip}")
        
        return VisualizeResponse(
            metadata=result['metadata'],
            visualization=result['visualization'],
            linesync=result['linesync'],
            execution_output=execution_output,
            is_fallback=is_fallback
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        # Code validation errors
        logger.warning(f"Validation error for {client_ip}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected error during visualization for {client_ip}")
        raise HTTPException(
            status_code=500,
            detail=f"Visualization service error: {str(e)}"
        )


@router.get("/health")
async def health():
    """
    Health check endpoint.
    
    Checks:
    - API is running
    - Gemini API is accessible
    """
    try:
        gemini_healthy = await health_check()
        
        return {
            "status": "healthy" if gemini_healthy else "degraded",
            "gemini_api": "connected" if gemini_healthy else "unavailable",
            "message": "Service is operational" if gemini_healthy else "AI service degraded"
        }
    except Exception as e:
        logger.exception("Health check failed")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@router.get("/limits")
async def get_rate_limits():
    """Get current rate limit configuration"""
    return {
        "compile": {
            "max_requests": 20,
            "window_seconds": 60,
            "description": "20 compilation requests per minute"
        },
        "visualize": {
            "max_requests": 10,
            "window_seconds": 60,
            "description": "10 visualization requests per minute"
        },
        "code_limits": {
            "max_lines": 100,
            "max_size_bytes": 50000,
            "execution_timeout_seconds": 10,
            "compilation_timeout_seconds": 10
        }
    }
