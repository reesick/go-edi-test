"""
AI Explainer - Generates adaptive explanations using Google Gemini
"""
import os
import json
import google.generativeai as genai
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=api_key)

# Load system prompt
prompt_path = os.path.join(os.path.dirname(__file__), "adapters", "prompt_system.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    SYSTEM_PROMPT = f.read()


def explain_step(frame: Dict[str, Any], user_behavior: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate adaptive explanation for a single algorithm step.
    
    Args:
        frame: Trace frame with stepIndex, array, pointers, action, etc.
        user_behavior: User behavior signals (pauseDuration, replayCount, etc.)
        
    Returns:
        Dictionary with: mode, explanation, short_hint, confidence_estimate, followup_question
    """
    # Merge frame and user_behavior into input JSON
    input_data = {**frame, "userBehavior": user_behavior}
    
    # Build the prompt
    user_message = json.dumps(input_data, indent=2)
    
    # Create model
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 1024,
        }
    )
    
    # Call Gemini with retry logic
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Start chat with system prompt
            chat = model.start_chat(history=[
                {"role": "user", "parts": [SYSTEM_PROMPT]},
                {"role": "model", "parts": ["I understand. I will generate adaptive algorithm explanations in strict JSON format based on the provided context and user behavior signals."]}
            ])
            
            # Send the frame data
            response = chat.send_message(user_message)
            response_text = response.text.strip()
            
            # Try to parse JSON
            # Remove code fences if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])  # Remove first and last line
            
            result = json.loads(response_text)
            
            # Validate required fields
            required_fields = ["mode", "explanation", "short_hint", "confidence_estimate", "followup_question"]
            if all(field in result for field in required_fields):
                return result
            else:
                raise ValueError(f"Missing required fields in response: {result}")
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                # Return fallback response
                return {
                    "mode": "conceptual",
                    "explanation": "This step moves the array closer to sorted order by comparing and possibly reordering neighboring values.",
                    "short_hint": "Look at which two values are being compared or swapped.",
                    "confidence_estimate": "medium",
                    "followup_question": "Which value do you expect to move toward the end after a few more steps?"
                }
    
    # Should never reach here
    return {
        "mode": "conceptual",
        "explanation": "Processing this step...",
        "short_hint": "Watch the visualization",
        "confidence_estimate": "low",
        "followup_question": ""
    }
