"""
Concept Tracker - Tracks mastery of algorithm concepts
"""
from typing import Dict, List
from session_manager import get_session_manager


# Define concepts for each algorithm
ALGORITHM_CONCEPTS = {
    "bubble_sort": {
        "comparisons": {"weight": 0.20, "threshold": 0.8},
        "swaps": {"weight": 0.20, "threshold": 0.8},
        "nested_loops": {"weight": 0.15, "threshold": 0.7},
        "pointer_movement": {"weight": 0.10, "threshold": 0.7},
        "time_complexity": {"weight": 0.15, "threshold": 0.7},
        "space_complexity": {"weight": 0.10, "threshold": 0.7},
        "optimization": {"weight": 0.05, "threshold": 0.6},
        "edge_cases": {"weight": 0.05, "threshold": 0.6}
    },
    "quick_sort": {
        "pivot_selection": {"weight": 0.25, "threshold": 0.8},
        "partitioning": {"weight": 0.25, "threshold": 0.8},
        "recursion": {"weight": 0.20, "threshold": 0.7},
        "time_complexity": {"weight": 0.15, "threshold": 0.7},
        "space_complexity": {"weight": 0.10, "threshold": 0.7},
        "stability": {"weight": 0.05, "threshold": 0.6}
    }
}


class ConceptTracker:
    """
    Tracks and calculates concept mastery scores.
    Provides weak concept identification and learning recommendations.
    """
    
    def __init__(self):
        self.session_manager = get_session_manager()
    
    def get_concepts(self, algorithm: str) -> List[str]:
        """Get list of concepts for an algorithm"""
        return list(ALGORITHM_CONCEPTS.get(algorithm, {}).keys())
    
    def calculate_mastery(
        self,
        session_id: str,
        algorithm: str,
        concept_name: str,
        performance_data: Dict
    ) -> float:
        """
        Calculate mastery score based on performance.
        
        performance_data format:
        {
            "correct_answers": 3,
            "total_attempts": 4,
            "time_spent": 120,  # seconds
            "replays": 1
        }
        """
        if concept_name not in ALGORITHM_CONCEPTS.get(algorithm, {}):
            return 0.0
        
        # Base score from accuracy
        correct = performance_data.get("correct_answers", 0)
        total = performance_data.get("total_attempts", 1)
        accuracy_score = correct / total if total > 0 else 0.0
        
        # Adjust for replays (more replays = lower mastery)
        replays = performance_data.get("replays", 0)
        replay_penalty = max(0, 1 - (replays * 0.1))
        
        # Adjust for time (faster = higher mastery, within reason)
        time_spent = performance_data.get("time_spent", 60)
        optimal_time = 30  # seconds per question
        time_factor = min(1.0, optimal_time / max(time_spent / total, 1))
        
        # Weighted combination
        score = (
            accuracy_score * 0.6 +
            replay_penalty * 0.2 +
            time_factor * 0.2
        )
        
        # Get current score and blend (gradual improvement)
        session = self.session_manager.get_session(session_id)
        current_score = 0.0
        
        if session and algorithm in session.get("conceptMastery", {}):
            current_score = session["conceptMastery"][algorithm].get(concept_name, 0.0)
        
        # Weighted average (30% current, 70% new performance)
        final_score = (current_score * 0.3) + (score * 0.7)
        
        # Update in database
        self.session_manager.update_concept_mastery(
            session_id, algorithm, concept_name, final_score
        )
        
        return round(final_score, 2)
    
    def get_weak_concepts(
        self,
        session_id: str,
        algorithm: str,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Get concepts below threshold (weak areas).
        Returns list sorted by weakest first.
        """
        session = self.session_manager.get_session(session_id)
        if not session:
            return []
        
        mastery = session.get("conceptMastery", {}).get(algorithm, {})
        concepts = ALGORITHM_CONCEPTS.get(algorithm, {})
        
        weak = []
        for concept_name, config in concepts.items():
            score = mastery.get(concept_name, 0.0)
            if score < threshold:
                weak.append({
                    "concept": concept_name,
                    "score": score,
                    "weight": config["weight"],
                    "threshold": config["threshold"]
                })
        
        # Sort by score (weakest first)
        weak.sort(key=lambda x: x["score"])
        
        return weak
    
    def get_mastered_concepts(
        self,
        session_id: str,
        algorithm: str
    ) -> List[str]:
        """Get concepts that have been mastered (>= threshold)"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return []
        
        mastery = session.get("conceptMastery", {}).get(algorithm, {})
        concepts = ALGORITHM_CONCEPTS.get(algorithm, {})
        
        mastered = []
        for concept_name, config in concepts.items():
            score = mastery.get(concept_name, 0.0)
            if score >= config["threshold"]:
                mastered.append(concept_name)
        
        return mastered
    
    def get_average_mastery(self, session_id: str, algorithm: str) -> float:
        """Calculate weighted average mastery for an algorithm"""
        session = self.session_manager.get_session(session_id)
        if not session:
            return 0.0
        
        mastery = session.get("conceptMastery", {}).get(algorithm, {})
        concepts = ALGORITHM_CONCEPTS.get(algorithm, {})
        
        if not concepts:
            return 0.0
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for concept_name, config in concepts.items():
            score = mastery.get(concept_name, 0.0)
            weight = config["weight"]
            total_weighted_score += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return round(total_weighted_score / total_weight, 2)
    
    def recommend_focus_areas(
        self,
        session_id: str,
        algorithm: str,
        max_areas: int = 3
    ) -> List[str]:
        """
        Recommend which concepts to focus on next.
        Returns top priority concepts.
        """
        weak = self.get_weak_concepts(session_id, algorithm)
        
        # Sort by importance (weight * gap from threshold)
        weak.sort(
            key=lambda x: x["weight"] * (x["threshold"] - x["score"]),
            reverse=True
        )
        
        return [c["concept"] for c in weak[:max_areas]]


# Singleton
_concept_tracker = None

def get_concept_tracker() -> ConceptTracker:
    """Get or create concept tracker instance"""
    global _concept_tracker
    if _concept_tracker is None:
        _concept_tracker = ConceptTracker()
    return _concept_tracker
