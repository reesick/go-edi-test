"""
Preset Manager - Manages code presets and custom code storage
"""
import os
from typing import Dict, List, Optional


# Preset metadata
PRESETS = {
    "bubble_sort": {
        "name": "Bubble Sort",
        "description": "Classic bubble sort - compares adjacent elements",
        "difficulty": "beginner",
        "file": "bubble_sort.py"
    },
    "quick_sort": {
        "name": "Quick Sort",
        "description": "Divide and conquer with pivot selection",
        "difficulty": "intermediate",
        "file": "quick_sort.py"
    },
    "merge_sort": {
        "name": "Merge Sort",
        "description": "Divide and conquer with merge operation",
        "difficulty": "intermediate",
        "file": "merge_sort.py"
    }
}


class PresetManager:
    """Manages loading and saving algorithm code presets"""
    
    def __init__(self, presets_dir: str = "presets"):
        self.presets_dir = presets_dir
        
    def list_presets(self) -> List[Dict]:
        """Get all available presets"""
        presets_list = []
        for key, meta in PRESETS.items():
            presets_list.append({
                "id": key,
                "name": meta["name"],
                "description": meta["description"],
                "difficulty": meta["difficulty"]
            })
        return presets_list
    
    def get_preset(self, preset_id: str) -> Optional[Dict]:
        """Load a specific preset's code"""
        if preset_id not in PRESETS:
            return None
        
        meta = PRESETS[preset_id]
        filepath = os.path.join(self.presets_dir, meta["file"])
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                code = f.read()
            
            return {
                "id": preset_id,
                "name": meta["name"],
                "description": meta["description"],
                "difficulty": meta["difficulty"],
                "code": code
            }
        except FileNotFoundError:
            return None
    
    def save_custom_code(
        self,
        session_id: str,
        code: str,
        name: Optional[str] = None
    ) -> Dict:
        """Save user's custom code (future: to database)"""
        # For now, just return success
        # In future, save to database linked to session
        return {
            "success": True,
            "message": "Custom code saved",
            "sessionId": session_id
        }


# Singleton
_preset_manager = None

def get_preset_manager() -> PresetManager:
    """Get or create preset manager instance"""
    global _preset_manager
    if _preset_manager is None:
        _preset_manager = PresetManager()
    return _preset_manager
