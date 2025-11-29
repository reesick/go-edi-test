"""
Session Manager - Handles user sessions and progress tracking
"""
import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
import uuid


class SessionManager:
    """
    Manages user sessions with SQLite persistence.
    Tracks progress, concept mastery, and learning analytics.
    """
    
    def __init__(self, db_path: str = "database/sessions.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                created_at TEXT,
                updated_at TEXT,
                current_mode TEXT DEFAULT 'learn',
                current_algorithm TEXT,
                difficulty_level INTEGER DEFAULT 1,
                total_time INTEGER DEFAULT 0,
                questions_answered INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0.0
            )
        """)
        
        # Concept mastery table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concept_mastery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                algorithm TEXT,
                concept_name TEXT,
                mastery_score REAL DEFAULT 0.0,
                last_updated TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        # Session history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                event_type TEXT,
                event_data TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def create_session(self, user_id: str = None) -> Dict[str, Any]:
        """Create a new session"""
        session_id = str(uuid.uuid4())
        user_id = user_id or f"user_{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sessions 
            (session_id, user_id, created_at, updated_at)
            VALUES (?, ?, ?, ?)
        """, (session_id, user_id, now, now))
        
        conn.commit()
        conn.close()
        
        # Log session creation
        self._log_event(session_id, "session_created", {})
        
        return {
            "sessionId": session_id,
            "userId": user_id,
            "createdAt": now,
            "mode": "learn",
            "difficultyLevel": 1
        }
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get main session data
        cursor.execute("""
            SELECT * FROM sessions WHERE session_id = ?
        """, (session_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        session_data = dict(row)
        
        # Get concept mastery
        cursor.execute("""
            SELECT algorithm, concept_name, mastery_score
            FROM concept_mastery
            WHERE session_id = ?
        """, (session_id,))
        
        concepts = {}
        for row in cursor.fetchall():
            algo = row[0]
            if algo not in concepts:
                concepts[algo] = {}
            concepts[algo][row[1]] = row[2]
        
        conn.close()
        
        return {
            "sessionId": session_data["session_id"],
            "userId": session_data["user_id"],
            "currentMode": session_data["current_mode"],
            "currentAlgorithm": session_data["current_algorithm"],
            "difficultyLevel": session_data["difficulty_level"],
            "conceptMastery": concepts,
            "stats": {
                "totalTime": session_data["total_time"],
                "questionsAnswered": session_data["questions_answered"],
                "accuracy": session_data["accuracy"]
            },
            "createdAt": session_data["created_at"],
            "updatedAt": session_data["updated_at"]
        }
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically
        allowed_fields = [
            "current_mode", "current_algorithm", "difficulty_level",
            "total_time", "questions_answered", "accuracy"
        ]
        
        update_parts = []
        values = []
        
        for field in allowed_fields:
            if field in updates:
                update_parts.append(f"{field} = ?")
                values.append(updates[field])
        
        if not update_parts:
            conn.close()
            return False
        
        # Always update timestamp
        update_parts.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(session_id)
        
        query = f"""
            UPDATE sessions
            SET {', '.join(update_parts)}
            WHERE session_id = ?
        """
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        # Log update
        self._log_event(session_id, "session_updated", updates)
        
        return True
    
    def update_concept_mastery(
        self,
        session_id: str,
        algorithm: str,
        concept_name: str,
        score: float
    ):
        """Update mastery score for a specific concept"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        # Check if exists
        cursor.execute("""
            SELECT id FROM concept_mastery
            WHERE session_id = ? AND algorithm = ? AND concept_name = ?
        """, (session_id, algorithm, concept_name))
        
        if cursor.fetchone():
            # Update existing
            cursor.execute("""
                UPDATE concept_mastery
                SET mastery_score = ?, last_updated = ?
                WHERE session_id = ? AND algorithm = ? AND concept_name = ?
            """, (score, now, session_id, algorithm, concept_name))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO concept_mastery
                (session_id, algorithm, concept_name, mastery_score, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, algorithm, concept_name, score, now))
        
        conn.commit()
        conn.close()
    
    def get_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get session analytics"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get event history
        cursor.execute("""
            SELECT event_type, COUNT(*) as count
            FROM session_history
            WHERE session_id = ?
            GROUP BY event_type
        """, (session_id,))
        
        events = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        # Calculate average mastery
        avg_mastery = 0.0
        total_concepts = 0
        
        for algo_concepts in session["conceptMastery"].values():
            for score in algo_concepts.values():
                avg_mastery += score
                total_concepts += 1
        
        if total_concepts > 0:
            avg_mastery /= total_concepts
        
        return {
            "sessionId": session_id,
            "averageMastery": round(avg_mastery, 2),
            "totalConcepts": total_concepts,
            "events": events,
            "stats": session["stats"]
        }
    
    def _log_event(self, session_id: str, event_type: str, event_data: Dict):
        """Log an event to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO session_history
            (session_id, timestamp, event_type, event_data)
            VALUES (?, ?, ?, ?)
        """, (
            session_id,
            datetime.utcnow().isoformat(),
            event_type,
            json.dumps(event_data)
        ))
        
        conn.commit()
        conn.close()


# Singleton instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get or create session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
