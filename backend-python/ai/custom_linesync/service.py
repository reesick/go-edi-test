"""
Gemini AI Service for Custom Code LineSync

Production-grade AI service with retry logic, fallback handling,
and strict validation for generating visualizations and line synchronization.
"""

import json
import logging
import os
from typing import Dict, Any, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from pydantic import ValidationError
import google.generativeai as genai

from .models import (
    GeminiResponse,
    FallbackVisualization,
    LineSyncMapping,
    VisualizationFrame
)
from .prompts import (
    build_system_prompt,
    build_user_prompt,
    get_generation_config,
    sanitize_gemini_response
)

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not found in environment variables")


class GeminiServiceError(Exception):
    """Custom exception for Gemini service errors"""
    pass


class ValidationFailedError(Exception):
    """Exception for validation failures"""
    pass


def validate_linesync_against_code(linesync_data: Dict, code: str) -> bool:
    """
    Validate that all line numbers in linesync data exist in the code.
    
    Args:
        linesync_data: LineSync data from AI
        code: Original source code
    
    Returns:
        True if valid, False otherwise
    """
    total_lines = len(code.splitlines())
    
    # Check setup lines
    for line_num in linesync_data.get('setup_lines', []):
        if line_num < 1 or line_num > total_lines:
            logger.warning(f"Invalid setup line number: {line_num} (total lines: {total_lines})")
            return False
    
    # Check frame mappings
    for mapping in linesync_data.get('frame_mappings', []):
        for line_num in mapping.get('line_numbers', []):
            if line_num < 1 or line_num > total_lines:
                logger.warning(f"Invalid line number in mapping: {line_num} (total lines: {total_lines})")
                return False
    
    # Check non-visualized lines
    for line_num in linesync_data.get('non_visualized_lines', []):
        if line_num < 1 or line_num > total_lines:
            logger.warning(f"Invalid non-visualized line: {line_num} (total lines: {total_lines})")
            return False
    
    return True


def sanitize_linesync_data(linesync_data: Dict, code: str) -> Dict:
    """
    Remove invalid line numbers from linesync data.
    
    Args:
        linesync_data: LineSync data to sanitize
        code: Original source code
    
    Returns:
        Sanitized linesync data
    """
    total_lines = len(code.splitlines())
    
    # Filter setup lines
    linesync_data['setup_lines'] = [
        line for line in linesync_data.get('setup_lines', [])
        if 1 <= line <= total_lines
    ]
    
    # Filter frame mappings
    sanitized_mappings = []
    for mapping in linesync_data.get('frame_mappings', []):
        valid_lines = [
            line for line in mapping.get('line_numbers', [])
            if 1 <= line <= total_lines
        ]
        if valid_lines:  # Only keep mappings with at least one valid line
            mapping['line_numbers'] = valid_lines
            sanitized_mappings.append(mapping)
    
    linesync_data['frame_mappings'] = sanitized_mappings
    
    # Filter non-visualized lines
    linesync_data['non_visualized_lines'] = [
        line for line in linesync_data.get('non_visualized_lines', [])
        if 1 <= line <= total_lines
    ]
    
    return linesync_data


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((GeminiServiceError, ValidationFailedError)),
    reraise=True
)
async def call_gemini_with_retry(
    code: str,
    input_data: str,
    execution_output: str = ""
) -> Dict[str, Any]:
    """
    Call Gemini API with retry logic.
    
    Args:
        code: C++ source code
        input_data: Input data for the code
        execution_output: Output from executing the code
    
    Returns:
        Validated response dict
    
    Raises:
        GeminiServiceError: If API call fails
        ValidationFailedError: If response validation fails
    """
    try:
        # Build prompts
        system_prompt = build_system_prompt()
        user_prompt = build_user_prompt(code, input_data, execution_output)
        
        # Create model
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_prompt
        )
        
        # Generate content
        logger.info(f"Calling Gemini {GEMINI_MODEL} for code analysis...")
        response = await model.generate_content_async(
            user_prompt,
            generation_config=get_generation_config()
        )
        
        # Extract response text
        if not response or not response.text:
            raise GeminiServiceError("Empty response from Gemini API")
        
        # Sanitize response
        sanitized = sanitize_gemini_response(response.text)
        
        # Parse JSON
        try:
            response_json = json.loads(sanitized)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response text: {sanitized[:500]}")
            raise ValidationFailedError(f"Invalid JSON response: {str(e)}")
        
        # Validate structure with Pydantic
        try:
            validated = GeminiResponse(**response_json)
        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {e}")
            raise ValidationFailedError(f"Response validation failed: {str(e)}")
        
        # Business logic validation
        response_dict = validated.dict()
        if not validate_linesync_against_code(response_dict['linesync'], code):
            logger.warning("LineSync data contains invalid line numbers, sanitizing...")
            response_dict['linesync'] = sanitize_linesync_data(response_dict['linesync'], code)
        
        logger.info(f"Successfully validated Gemini response with {len(response_dict['visualization']['frames'])} frames")
        return response_dict
    
    except ValidationFailedError:
        raise  # Re-raise for retry
    except GeminiServiceError:
        raise  # Re-raise for retry
    except Exception as e:
        logger.exception("Unexpected error calling Gemini API")
        raise GeminiServiceError(f"Gemini API error: {str(e)}")


def generate_fallback_visualization(code: str, error_msg: str) -> Dict[str, Any]:
    """
    Generate a basic fallback visualization when AI fails.
    
    Args:
        code: Source code
        error_msg: Error message to include
    
    Returns:
        Fallback visualization dict
    """
    logger.warning("Generating fallback visualization due to AI failure")
    
    return {
        "metadata": {
            "total_frames": 1,
            "complexity": "unknown",
            "data_structures_used": ["unknown"],
            "is_fallback": True,
            "error": error_msg
        },
        "visualization": {
            "frames": [
                {
                    "frame_id": 0,
                    "timestamp_ms": 0,
                    "description": "AI visualization failed. Please check your code and try again.",
                    "arrays": [],
                    "variables": [],
                    "pointers": [],
                    "trees": [],
                    "graphs": [],
                    "stacks": [],
                    "queues": []
                }
            ]
        },
        "linesync": {
            "setup_lines": [],
            "frame_mappings": [
                {
                    "frame_id": 0,
                    "line_numbers": [1],
                    "code_snippet": "Unable to generate line sync",
                    "explanation": f"Visualization failed: {error_msg}",
                    "highlight_type": "default"
                }
            ],
            "non_visualized_lines": []
        }
    }


async def generate_visualization_and_linesync(
    code: str,
    input_data: str = "",
    execution_output: str = ""
) -> Dict[str, Any]:
    """
    Main entry point for generating visualization and linesync data.
    
    This is the production-grade function with full error handling and fallback.
    
    Args:
        code: C++ source code (max 100 lines)
        input_data: Input data for the algorithm
        execution_output: Output from executing the code
    
    Returns:
        Dict with visualization and linesync data
    
    Raises:
        ValueError: If code exceeds 100 lines
    """
    # Validate code length
    lines = code.splitlines()
    if len(lines) > 100:
        raise ValueError(f"Code exceeds maximum 100 lines (got {len(lines)} lines)")
    
    try:
        # Call Gemini with retry logic
        result = await call_gemini_with_retry(code, input_data, execution_output)
        return result
    
    except (GeminiServiceError, ValidationFailedError) as e:
        # All retries exhausted, return fallback
        logger.error(f"All retry attempts failed: {e}")
        return generate_fallback_visualization(code, str(e))
    
    except Exception as e:
        # Unexpected error, return fallback
        logger.exception("Unexpected error in visualization generation")
        return generate_fallback_visualization(code, f"Unexpected error: {str(e)}")


async def health_check() -> bool:
    """
    Check if Gemini API is accessible.
    
    Returns:
        True if API is healthy, False otherwise
    """
    try:
        if not GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not configured")
            return False
        
        model = genai.GenerativeModel(model_name=GEMINI_MODEL)
        response = await model.generate_content_async(
            "Hello",
            generation_config={"max_output_tokens": 10}
        )
        return bool(response and response.text)
    
    except Exception as e:
        logger.error(f"Gemini health check failed: {e}")
        return False
