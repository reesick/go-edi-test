"""C++ Compiler Service - Compiles and executes user's C++ code"""
import subprocess
import os
import json
import tempfile
import uuid
from pathlib import Path

class CPPCompiler:
    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "cpp_templates"
        self.temp_dir = Path(__file__).parent.parent / "cpp_temp"
        self.temp_dir.mkdir(exist_ok=True)
        
    def validate_syntax(self, code):
        """Validate C++ syntax by attempting compilation"""
        try:
            # Create temp file
            temp_id = str(uuid.uuid4())[:8]
            cpp_file = self.temp_dir / f"validate_{temp_id}.cpp"
            
            # Build complete code with header
            full_code = f"""#include <TrackedArray.h>

{code}
"""
            
            # Write test code
            with open(cpp_file, 'w') as f:
                f.write(full_code)
            
            # Try to compile (syntax check only) with include path
            result = subprocess.run(
                ['g++', '-std=c++17', f'-I{self.templates_dir}', '-fsyntax-only', str(cpp_file)],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Cleanup
            cpp_file.unlink(missing_ok=True)
            
            if result.returncode == 0:
                return {"valid": True}
            else:
                # Parse error
                error_msg = result.stderr
                line_num = self._extract_line_number(error_msg)
                # Adjust line number (subtract header lines)
                if line_num and line_num > 2:
                    line_num -= 2
                return {
                    "valid": False,
                    "error": error_msg,
                    "line": line_num
                }
                
        except subprocess.TimeoutExpired:
            return {"valid": False, "error": "Compilation timeout"}
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def compile_and_execute(self, user_code, module_type, function_name, initial_data):
        """Compile C++ code and execute it with tracking"""
        try:
            # Generate unique ID
            temp_id = str(uuid.uuid4())[:8]
            cpp_file = self.temp_dir / f"user_{temp_id}.cpp"
            exe_file = self.temp_dir / f"user_{temp_id}.exe"
            
            # Load template
            template_code = self._build_template(user_code, module_type, function_name, initial_data)
            
            # Write to file
            with open(cpp_file, 'w') as f:
                f.write(template_code)
            
            # Compile
            compile_result = subprocess.run(
                [
                    'g++',
                    '-std=c++17',
                    f'-I{self.templates_dir}',
                    str(cpp_file),
                    '-o', str(exe_file)
                ],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if compile_result.returncode != 0:
                # Compilation failed
                cpp_file.unlink(missing_ok=True)
                return {
                    "success": False,
                    "error": compile_result.stderr,
                    "type": "compilation"
                }
            
            # Execute
            exec_result = subprocess.run(
                [str(exe_file)],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # Cleanup
            cpp_file.unlink(missing_ok=True)
            exe_file.unlink(missing_ok=True)
            
            # Parse JSON output
            try:
                trace_data = json.loads(exec_result.stdout)
                return {
                    "success": True,
                    "trace": trace_data.get("trace", []),
                    "stdout": exec_result.stdout,
                    "stderr": exec_result.stderr
                }
            except json.JSONDecodeError as e:
                return {
                    "success": False,
                    "error": f"Failed to parse output: {str(e)}",
                    "stdout": exec_result.stdout,
                    "stderr": exec_result.stderr,
                    "type": "runtime"
                }
                
        except subprocess.TimeoutExpired:
            # Cleanup
            cpp_file.unlink(missing_ok=True)
            exe_file.unlink(missing_ok=True)
            return {"success": False, "error": "Execution timeout", "type": "runtime"}
        except Exception as e:
            return {"success": False, "error": str(e), "type": "system"}
    
    def _build_template(self, user_code, module_type, function_name, initial_data):
        """Build complete C++ code from template"""
        if module_type == "sorting" or module_type == "array":
            header = "#include <TrackedArray.h>"
            tracked_type = "TrackedArray"
            init_data = "{" + ",".join(map(str, initial_data)) + "}"
            # For searching, add target parameter
            if module_type == "searching":
                target_value = initial_data[len(initial_data) // 2] if initial_data else 5
                function_call = f"{function_name}(arr, {target_value});"
            else:
                function_call = f"{function_name}(arr);"
        elif module_type == "searching":
            header = "#include <TrackedArray.h>"
            tracked_type = "TrackedArray"
            init_data = "{" + ",".join(map(str, initial_data)) + "}"
            # Searching needs target value (use middle element)
            target_value = initial_data[len(initial_data) // 2] if initial_data else 5
            function_call = f"{function_name}(arr, {target_value});"
        else:
            # For now, default to TrackedArray
            header = "#include <TrackedArray.h>"
            tracked_type = "TrackedArray"
            init_data = "{" + ",".join(map(str, initial_data)) + "}"
            function_call = f"{function_name}(arr);"
        
        template = f"""
{header}
#include <vector>

// USER CODE
{user_code}

int main() {{
    // Create tracked structure
    std::vector<int> data = {init_data};
    {tracked_type} arr(data);
    
    // Call user function
    {function_call}
    
    // Output trace
    arr.print_trace();
    
    return 0;
}}
"""
        return template
    
    def _extract_line_number(self, error_msg):
        """Extract line number from compiler error"""
        import re
        match = re.search(r':(\d+):\d+:', error_msg)
        if match:
            return int(match.group(1))
        return None


# Global instance
cpp_compiler = CPPCompiler()
