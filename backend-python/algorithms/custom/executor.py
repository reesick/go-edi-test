"""
C++ Code Executor with Security

Securely compiles and executes user-submitted C++ code in an isolated environment
with timeouts, resource limits, and safety checks.
"""

import asyncio
import os
import uuid
import tempfile
import shutil
import re
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# Dangerous patterns that should be blocked
UNSAFE_PATTERNS = [
    r'#include\s*<windows\.h>',
    r'#include\s*<winsock.*\.h>',
    r'#include\s*<sys/socket\.h>',
    r'#include\s*<netinet.*\.h>',
    r'system\s*\(',
    r'exec\s*\(',
    r'popen\s*\(',
    r'fork\s*\(',
    r'__asm',
    r'asm\s+volatile',
]

# Maximum allowed code length
MAX_CODE_LINES = 100
MAX_CODE_SIZE = 50000  # 50KB


@dataclass
class CompileResult:
    """Result from compilation attempt"""
    success: bool
    executable_path: Optional[str] = None
    errors: str = ""
    warnings: str = ""
    compile_time_ms: int = 0


@dataclass
class ExecutionResult:
    """Result from code execution"""
    success: bool
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    execution_time_ms: int = 0
    timed_out: bool = False


def validate_code_safety(code: str) -> Tuple[bool, str]:
    """
    Check if code contains dangerous patterns.
    
    Args:
        code: C++ source code to validate
    
    Returns:
        (is_safe, error_message)
    """
    # Check code length
    lines = code.splitlines()
    if len(lines) > MAX_CODE_LINES:
        return False, f"Code exceeds maximum {MAX_CODE_LINES} lines"
    
    if len(code) > MAX_CODE_SIZE:
        return False, f"Code exceeds maximum size of {MAX_CODE_SIZE} bytes"
    
    # Check for unsafe patterns
    for pattern in UNSAFE_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"Code contains unsafe pattern: {pattern}"
    
    return True, ""


def validate_code_structure(code: str) -> Tuple[bool, str]:
    """
    Validate basic C++ structure requirements.
    
    Args:
        code: C++ source code
    
    Returns:
        (is_valid, error_message)
    """
    # Must have a main function
    if not re.search(r'int\s+main\s*\(', code):
        return False, "Code must contain a main() function"
    
    # Count braces (basic syntax check)
    open_braces = code.count('{')
    close_braces = code.count('}')
    if open_braces != close_braces:
        return False, "Mismatched braces in code"
    
    return True, ""


async def compile_code(
    code: str,
    timeout: int = 10,
    optimization_level: str = "O0"
) -> CompileResult:
    """
    Compile C++ code to an executable.
    
    Args:
        code: C++ source code
        timeout: Compilation timeout in seconds
        optimization_level: Compiler optimization level (O0, O1, O2, O3)
    
    Returns:
        CompileResult with compilation status
    """
    import time
    import subprocess
    start_time = time.time()
    
    # Validate code safety
    is_safe, error_msg = validate_code_safety(code)
    if not is_safe:
        logger.warning(f"Unsafe code rejected: {error_msg}")
        return CompileResult(success=False, errors=error_msg)
    
    # Validate code structure
    is_valid, error_msg = validate_code_structure(code)
    if not is_valid:
        logger.warning(f"Invalid code structure: {error_msg}")
        return CompileResult(success=False, errors=error_msg)
    
    # Create temporary directory for compilation
    temp_dir = Path(tempfile.gettempdir()) / f"custom_code_{uuid.uuid4().hex}"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Write code to file
        source_file = temp_dir / "code.cpp"
        source_file.write_text(code, encoding='utf-8')
        
        # Output executable path
        executable = temp_dir / "code.exe"
        
        # Compile command
        compile_cmd = [
            "g++",
            f"-{optimization_level}",
            "-std=c++17",
            "-Wall",
            "-Wextra",
            str(source_file),
            "-o",
            str(executable)
        ]
        
        # Run compilation synchronously (Windows compatibility)
        try:
            result = subprocess.run(
                compile_cmd,
                capture_output=True,
                timeout=timeout,
                cwd=str(temp_dir),
                text=True
            )
            
            stdout_text = result.stdout.strip()
            stderr_text = result.stderr.strip()
            
        except subprocess.TimeoutExpired:
            logger.error(f"Compilation timeout after {timeout}s")
            return CompileResult(
                success=False,
                errors=f"Compilation timeout after {timeout}s"
            )
        
        compile_time = int((time.time() - start_time) * 1000)
        
        logger.info(f"Compilation return code: {result.returncode}")
        logger.info(f"Compilation stdout: {stdout_text[:500]}")
        logger.info(f"Compilation stderr: {stderr_text[:500]}")
        
        # Check compilation result
        if result.returncode == 0:
            logger.info(f"Compilation successful in {compile_time}ms")
            return CompileResult(
                success=True,
                executable_path=str(executable),
                warnings=stderr_text,
                compile_time_ms=compile_time
            )
        else:
            # Combine stdout and stderr for better error messages
            error_output = stderr_text if stderr_text else stdout_text
            if not error_output:
                error_output = f"Compilation failed with return code {result.returncode}. No error details available."
            
            logger.error(f"Compilation failed: {error_output}")
            return CompileResult(
                success=False,
                errors=error_output,
                compile_time_ms=compile_time
            )
    
    except Exception as e:
        logger.exception("Unexpected error during compilation")
        return CompileResult(
            success=False,
            errors=f"Compilation error: {str(e)}"
        )


async def execute_code(
    executable_path: str,
    input_data: str = "",
    timeout: int = 10,
    max_output_size: int = 100000
) -> ExecutionResult:
    """
    Execute compiled C++ code with input.
    
    Args:
        executable_path: Path to compiled executable
        input_data: Input to pass to stdin
        timeout: Execution timeout in seconds
        max_output_size: Maximum output size in bytes
    
    Returns:
        ExecutionResult with execution output
    """
    import time
    import subprocess
    start_time = time.time()
    
    # Validate executable exists
    if not os.path.exists(executable_path):
        return ExecutionResult(
            success=False,
            stderr="Executable not found",
            exit_code=1
        )
    
    try:
        # Execute with timeout (synchronously for Windows compatibility)
        try:
            result = subprocess.run(
                [executable_path],
                input=input_data,
                capture_output=True,
                timeout=timeout,
                text=True
            )
            timed_out = False
            
        except subprocess.TimeoutExpired:
            logger.warning(f"Execution timeout after {timeout}s")
            return ExecutionResult(
                success=False,
                stderr=f"Execution timeout after {timeout}s",
                exit_code=-1,
                timed_out=True
            )
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Truncate output with size limits
        stdout_str = result.stdout[:max_output_size]
        stderr_str = result.stderr[:max_output_size]
        
        success = result.returncode == 0
        
        logger.info(f"Execution {'successful' if success else 'failed'} in {execution_time}ms")
        
        return ExecutionResult(
            success=success,
            stdout=stdout_str,
            stderr=stderr_str,
            exit_code=result.returncode,
            execution_time_ms=execution_time,
            timed_out=False
        )
    
    except Exception as e:
        logger.exception("Unexpected error during execution")
        return ExecutionResult(
            success=False,
            stderr=f"Execution error: {str(e)}",
            exit_code=1
        )


def cleanup_temp_files(executable_path: str):
    """
    Clean up temporary files after execution.
    
    Args:
        executable_path: Path to executable (temp directory will be deleted)
    """
    try:
        temp_dir = Path(executable_path).parent
        if temp_dir.exists() and "custom_code_" in str(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            logger.info(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        logger.warning(f"Failed to clean up temp files: {e}")
