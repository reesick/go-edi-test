"""
Prompt Templates for Gemini 2.0 Flash

Carefully crafted prompts with strict schema enforcement,
few-shot examples, and validation rules to ensure high-quality output.
"""

import json
from typing import Dict, Any


# Minimal JSON Schema for Gemini compatibility
# Gemini has strict requirements - keep this as simple as possible
GEMINI_RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["metadata", "visualization", "linesync"],
    "properties": {
        "metadata": {
            "type": "object",
            "required": ["total_frames", "complexity", "data_structures_used"],
            "properties": {
                "total_frames": {"type": "integer"},
                "complexity": {"type": "string"},
                "data_structures_used": {"type": "array"}
            }
        },
        "visualization": {
            "type": "object",
            "required": ["frames"],
            "properties": {
                "frames": {
                    "type": "array"
                }
            }
        },
        "linesync": {
            "type": "object",
            "required": ["frame_mappings"],
            "properties": {
                "setup_lines": {"type": "array"},
                "frame_mappings": {"type": "array"},
                "non_visualized_lines": {"type": "array"}
            }
        }
    }
}


SYSTEM_PROMPT = """You are an expert C++ algorithm visualizer and code execution tracer.

Your task is to analyze C++ code and generate TWO things:
1. **Visualization frames** - Data structure states at each step
2. **Line synchronization** - Mapping each frame to source code line(s)

CRITICAL REQUIREMENTS:
- Output MUST be valid JSON matching the provided schema
- Frame IDs must be sequential starting from 0
- Line numbers must be 1-indexed and within 1-100 range
- Only map lines that cause VISUAL changes (skip setup, includes, return statements)
- Categorize lines as: setup, synced, or non-visualized
- Maximum 100 frames for performance
- Be accurate - trace execution carefully

DATA STRUCTURES YOU CAN VISUALIZE:
- Arrays/Vectors: horizontal bar layout
- Trees: hierarchical node layout with x,y coordinates
- Graphs: nodes with edges (directed/undirected)
- Stacks: vertical LIFO visualization
- Queues: horizontal FIFO visualization
- Variables: simple key-value pairs

HIGHLIGHT TYPES:
- "comparison" - comparing elements
- "modification" - changing values (swap, assignment)
- "assignment" - initial value assignment
- "condition" - if/while condition check
- "default" - other operations
"""


FEW_SHOT_EXAMPLES = """
EXAMPLE 1: Bubble Sort
--------------------------------------------------
CODE:
```cpp
int main() {
    int arr[] = {5, 2, 8, 1};
    int n = 4;
    
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (arr[j] > arr[j+1]) {
                swap(arr[j], arr[j+1]);
            }
        }
    }
}
```

OUTPUT:
{
  "metadata": {
    "total_frames": 3,
    "complexity": "low",
    "data_structures_used": ["array"]
  },
  "visualization": {
    "frames": [
      {
        "frame_id": 0,
        "description": "Initial array",
        "arrays": [{
          "name": "arr",
          "values": [5, 2, 8, 1],
          "type": "int",
          "highlights": {"indices": [0, 1], "colors": ["blue", "red"], "labels": ["j", "j+1"]}
        }],
        "variables": [{"name": "i", "value": 0, "type": "int"}, {"name": "j", "value": 0, "type": "int"}]
      },
      {
        "frame_id": 1,
        "description": "Swapping arr[0] and arr[1]",
        "arrays": [{
          "name": "arr",
          "values": [2, 5, 8, 1],
          "type": "int",
          "highlights": {"indices": [0, 1], "colors": ["yellow", "yellow"], "labels": ["swapped", "swapped"]}
        }],
        "variables": [{"name": "i", "value": 0, "type": "int"}, {"name": "j", "value": 0, "type": "int"}]
      },
      {
        "frame_id": 2,
        "description": "Comparing arr[2] and arr[3]",
        "arrays": [{
          "name": "arr",
          "values": [2, 5, 8, 1],
          "type": "int",
          "highlights": {"indices": [2, 3], "colors": ["blue", "red"], "labels": ["j", "j+1"]}
        }],
        "variables": [{"name": "i", "value": 0, "type": "int"}, {"name": "j", "value": 2, "type": "int"}]
      }
    ]
  },
  "linesync": {
    "setup_lines": [2, 3],
    "frame_mappings": [
      {
        "frame_id": 0,
        "line_numbers": [7],
        "code_snippet": "if (arr[j] > arr[j+1])",
        "explanation": "Comparing arr[0]=5 and arr[1]=2",
        "highlight_type": "comparison"
      },
      {
        "frame_id": 1,
        "line_numbers": [8],
        "code_snippet": "swap(arr[j], arr[j+1]);",
        "explanation": "Swapping because 5 > 2",
        "highlight_type": "modification"
      },
      {
        "frame_id": 2,
        "line_numbers": [7],
        "code_snippet": "if (arr[j] > arr[j+1])",
        "explanation": "Comparing arr[2]=8 and arr[3]=1",
        "highlight_type": "comparison"
      }
    ],
    "non_visualized_lines": [1, 4, 5, 6, 9, 10, 11, 12]
  }
}

EXAMPLE 2: Binary Search Tree Insert
--------------------------------------------------
CODE:
```cpp
struct Node {
    int val;
    Node* left, *right;
};

void insert(Node* root, int key) {
    if (root == nullptr) return;
    if (key < root->val) insert(root->left, key);
    else insert(root->right, key);
}
```

OUTPUT:
{
  "metadata": {
    "total_frames": 2,
    "complexity": "medium",
    "data_structures_used": ["tree"]
  },
  "visualization": {
    "frames": [
      {
        "frame_id": 0,
        "description": "Checking if 15 < 50 (root)",
        "trees": [{
          "name": "bst",
          "type": "binary_search_tree",
          "nodes": [
            {"id": 0, "value": 50, "x": 400, "y": 100, "highlighted": true, "color": "blue"},
            {"id": 1, "value": 30, "x": 300, "y": 200, "highlighted": false, "color": "default"}
          ]
        }],
        "variables": [{"name": "key", "value": 15, "type": "int"}]
      },
      {
        "frame_id": 1,
        "description": "Moving to left subtree",
        "trees": [{
          "name": "bst",
          "type": "binary_search_tree",
          "nodes": [
            {"id": 0, "value": 50, "x": 400, "y": 100, "highlighted": false, "color": "default"},
            {"id": 1, "value": 30, "x": 300, "y": 200, "highlighted": true, "color": "blue"}
          ]
        }],
        "variables": [{"name": "key", "value": 15, "type": "int"}]
      }
    ]
  },
  "linesync": {
    "setup_lines": [1, 2, 3, 4],
    "frame_mappings": [
      {
        "frame_id": 0,
        "line_numbers": [8],
        "code_snippet": "if (key < root->val)",
        "explanation": "Comparing 15 < 50, will go left",
        "highlight_type": "condition"
      },
      {
        "frame_id": 1,
        "line_numbers": [8],
        "code_snippet": "insert(root->left, key);",
        "explanation": "Recursing to left child",
        "highlight_type": "default"
      }
    ],
    "non_visualized_lines": [5, 6, 7, 9, 10]
  }
}
"""


def build_system_prompt() -> str:
    """Build the complete system prompt"""
    return SYSTEM_PROMPT


def build_user_prompt(code: str, input_data: str, execution_output: str = "") -> str:
    """
    Build the user prompt with code, input, and execution output.
    
    Args:
        code: User's C++ source code
        input_data: Input provided by user
        execution_output: Output from executing the code (if available)
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        "Analyze the following C++ code and generate visualization + linesync data.\n",
        "\n=== CODE ===\n```cpp\n",
        code,
        "\n```\n",
    ]
    
    if input_data:
        prompt_parts.extend([
            "\n=== INPUT ===\n",
            input_data,
            "\n"
        ])
    
    if execution_output:
        prompt_parts.extend([
            "\n=== EXECUTION OUTPUT ===\n",
            execution_output,
            "\n"
        ])
    
    prompt_parts.extend([
        "\n=== INSTRUCTIONS ===\n",
        "Generate a JSON response following the strict schema provided.\n",
        "Trace the execution step-by-step and create visualization frames.\n",
        "Map each frame to the exact source code line(s) that caused that state.\n",
        "\n=== REFERENCE EXAMPLES ===\n",
        FEW_SHOT_EXAMPLES,
        "\n=== YOUR OUTPUT (JSON Only) ===\n"
    ])
    
    return "".join(prompt_parts)


def get_generation_config() -> Dict[str, Any]:
    """
    Get Gemini API generation configuration.
    
    Returns:
        Configuration dict for Gemini API
    """
    return {
        "response_mime_type": "application/json",
        # Schema removed - Gemini has compatibility issues on Windows
        # Relying on prompt examples and Pydantic validation instead
        "temperature": 0.1,  # Low temperature for deterministic output
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }


def sanitize_gemini_response(response_text: str) -> str:
    """
    Sanitize Gemini response by removing markdown code fences and extra whitespace.
    
    Args:
        response_text: Raw response from Gemini
    
    Returns:
        Cleaned JSON string
    """
    # Remove markdown code fences
    text = response_text.strip()
    
    if text.startswith("```json"):
        text = text[7:]  # Remove ```json
    elif text.startswith("```"):
        text = text[3:]  # Remove ```
    
    if text.endswith("```"):
        text = text[:-3]  # Remove closing ```
    
    # Strip whitespace
    text = text.strip()
    
    return text
