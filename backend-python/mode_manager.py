"""
Mode Manager - Handles learning mode selection and configuration
"""
from typing import Dict, Any
from concept_tracker import get_concept_tracker


# Mode configurations
MODE_CONFIGS = {
    "learn": {
        "name": "Learn Mode",
        "description": "Beginner-friendly with detailed explanations",
        "array_size": (4, 5),
        "ai_detail": "high",
        "questions_per_session": 10,
        "hints_available": True,
        "hint_levels": 3,
        "time_limit": None,
        "required_mastery": 0.0
    },
    "practice": {
        "name": "Practice Mode",
        "description": "Reinforce understanding with focused practice",
        "array_size": (8, 10),
        "ai_detail": "medium",
        "questions_per_session": 5,
        "hints_available": True,
        "hint_levels": 2,
        "time_limit": None,
        "required_mastery": 0.5
    },
    "challenge": {
        "name": "Challenge Mode",
        "description": "Test mastery with edge cases",
        "array_size": (15, 20),
        "ai_detail": "low",
        "questions_per_session": 3,
        "hints_available": False,
        "hint_levels": 0,
        "time_limit": 600,  # 10 minutes
        "required_mastery": 0.8
    },
    "explore": {
        "name": "Explore Mode",
        "description": "Compare algorithms side-by-side",
        "array_size": (10, 15),
        "ai_detail": "comparative",
        "questions_per_session": 0,
        "hints_available": False,
        "hint_levels": 0,
        "time_limit": None,
        "required_mastery": 0.0
    },
    "debug": {
        "name": "Debug Mode",
        "description": "Fix broken code with guided hints",
        "array_size": (5, 8),
        "ai_detail": "step_by_step",
        "questions_per_session": 0,
        "hints_available": True,
        "hint_levels": 3,
        "time_limit": None,
        "required_mastery": 0.0
    }
}


class ModeManager:
    """
    Manages learning modes and recommendations.
    Auto-selects appropriate mode based on user progress.
    """
    
    def __init__(self):
        self.concept_tracker = get_concept_tracker()
    
    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """Get configuration for a specific mode"""
        return MODE_CONFIGS.get(mode, MODE_CONFIGS["learn"])
    
    def get_all_modes(self) -> Dict[str, Dict]:
        """Get all available modes"""
        return MODE_CONFIGS
    
    def recommend_mode(
        self,
        session_id: str,
        algorithm: str
    ) -> Dict[str, Any]:
        """
        Recommend best mode based on user progress.
        
        Logic:
        - avg_mastery < 0.5: Learn
        - 0.5 <= avg_mastery < 0.8: Practice
        - avg_mastery >= 0.8: Challenge
        - Can always choose Explore or Debug manually
        """
        avg_mastery = self.concept_tracker.get_average_mastery(
            session_id, algorithm
        )
        
        if avg_mastery < 0.5:
            recommended = "learn"
            reason = "Building foundational understanding"
        elif avg_mastery < 0.8:
            recommended = "practice"
            reason = "Reinforcing concepts and improving mastery"
        else:
            recommended = "challenge"
            reason = "Ready to test advanced scenarios"
        
        return {
            "recommendedMode": recommended,
            "reason": reason,
            "averageMastery": avg_mastery,
            "config": MODE_CONFIGS[recommended],
            "alternativeModes": {
                "explore": "Compare with other algorithms",
                "debug": "Practice fixing code errors"
            }
        }
    
    def can_access_mode(
        self,
        session_id: str,
        algorithm: str,
        mode: str
    ) -> Dict[str, Any]:
        """
        Check if user can access a specific mode.
        Returns access status and reason.
        """
        if mode not in MODE_CONFIGS:
            return {
                "canAccess": False,
                "reason": "Unknown mode"
            }
        
        # Explore and Debug always accessible
        if mode in ["explore", "debug"]:
            return {
                "canAccess": True,
                "reason": "Always available"
            }
        
        required_mastery = MODE_CONFIGS[mode]["required_mastery"]
        avg_mastery = self.concept_tracker.get_average_mastery(
            session_id, algorithm
        )
        
        if avg_mastery >= required_mastery:
            return {
                "canAccess": True,
                "reason": "Mastery requirement met",
                "yourMastery": avg_mastery,
                "requiredMastery": required_mastery
            }
        else:
            return {
                "canAccess": False,
                "reason": f"Need {int(required_mastery*100)}% mastery",
                "yourMastery": avg_mastery,
                "requiredMastery": required_mastery,
                "gap": round(required_mastery - avg_mastery, 2)
            }


# Singleton
_mode_manager = None

def get_mode_manager() -> ModeManager:
    """Get or create mode manager instance"""
    global _mode_manager
    if _mode_manager is None:
        _mode_manager = ModeManager()
    return _mode_manager
