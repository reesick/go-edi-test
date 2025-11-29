"""
FastAPI Backend for Algorithm Visualization
Endpoints:
  - POST /execute: Generate algorithm trace
  - POST /explain-step: Get AI explanation for a step
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import executor
import ai_explainer
from session_manager import get_session_manager
from mode_manager import get_mode_manager
from concept_tracker import get_concept_tracker
from batch_analyzer import get_batch_analyzer
from preset_manager import get_preset_manager

app = FastAPI(title="Algorithm Visualization Backend")

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ExecuteRequest(BaseModel):
    algorithmId: str
    array: List[int]


class ExecuteResponse(BaseModel):
    trace: List[Dict[str, Any]]


class ExplainStepRequest(BaseModel):
    frame: Dict[str, Any]
    userBehavior: Dict[str, Any]


class ExplainStepResponse(BaseModel):
    mode: str
    explanation: str
    short_hint: str
    confidence_estimate: str
    followup_question: str


# Endpoints
@app.post("/execute", response_model=ExecuteResponse)
async def execute_algorithm(request: ExecuteRequest):
    """
    Execute algorithm and return complete trace.
    """
    try:
        algorithm_id = request.algorithmId
        array = request.array
        
        # Validate input
        if not array:
            raise HTTPException(status_code=400, detail="Array cannot be empty")
        
        if not all(isinstance(x, int) for x in array):
            raise HTTPException(status_code=400, detail="Array must contain only integers")
        
        # Execute algorithm
        if algorithm_id == "bubble_sort":
            trace = executor.run_bubble_sort(array)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algorithm_id}")
        
        return ExecuteResponse(trace=trace)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/explain-step", response_model=ExplainStepResponse)
async def explain_algorithm_step(request: ExplainStepRequest):
    """
    Generate AI explanation for a single step.
    """
    try:
        frame = request.frame
        user_behavior = request.userBehavior
        
        # Generate explanation
        result = ai_explainer.explain_step(frame, user_behavior)
        
        return ExplainStepResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "python-backend"}


# ============================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================

class CreateSessionRequest(BaseModel):
    userId: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    currentMode: Optional[str] = None
    currentAlgorithm: Optional[str] = None
    difficultyLevel: Optional[int] = None
    totalTime: Optional[int] = None
    questionsAnswered: Optional[int] = None
    accuracy: Optional[float] = None


@app.post("/session/create")
async def create_session(request: CreateSessionRequest):
    """Create a new user session"""
    try:
        session_mgr = get_session_manager()
        session = session_mgr.create_session(request.userId)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session data"""
    try:
        session_mgr = get_session_manager()
        session = session_mgr.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/session/{session_id}")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update session progress"""
    try:
        session_mgr = get_session_manager()
        
        # Convert to snake_case for database
        updates = {}
        if request.currentMode:
            updates["current_mode"] = request.currentMode
        if request.currentAlgorithm:
            updates["current_algorithm"] = request.currentAlgorithm
        if request.difficultyLevel is not None:
            updates["difficulty_level"] = request.difficultyLevel
        if request.totalTime is not None:
            updates["total_time"] = request.totalTime
        if request.questionsAnswered is not None:
            updates["questions_answered"] = request.questionsAnswered
        if request.accuracy is not None:
            updates["accuracy"] = request.accuracy
        
        success = session_mgr.update_session(session_id, updates)
        
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get session analytics"""
    try:
        session_mgr = get_session_manager()
        stats = session_mgr.get_analytics(session_id)
        
        if not stats:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# MODE MANAGEMENT ENDPOINTS
# ============================================

class ModeRecommendRequest(BaseModel):
    sessionId: str
    algorithm: str


class ModeAccessRequest(BaseModel):
    sessionId: str
    algorithm: str
    mode: str


@app.get("/modes")
async def get_all_modes():
    """Get all available modes with configurations"""
    try:
        mode_mgr = get_mode_manager()
        return mode_mgr.get_all_modes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mode/recommend")
async def recommend_mode(request: ModeRecommendRequest):
    """Get recommended mode based on user progress"""
    try:
        mode_mgr = get_mode_manager()
        recommendation = mode_mgr.recommend_mode(
            request.sessionId,
            request.algorithm
        )
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mode/check-access")
async def check_mode_access(request: ModeAccessRequest):
    """Check if user can access a specific mode"""
    try:
        mode_mgr = get_mode_manager()
        access = mode_mgr.can_access_mode(
            request.sessionId,
            request.algorithm,
            request.mode
        )
        return access
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# CONCEPT TRACKING ENDPOINTS
# ============================================

class UpdateMasteryRequest(BaseModel):
    sessionId: str
    algorithm: str
    concept: str
    performanceData: Dict[str, Any]


class WeakAreasRequest(BaseModel):
    sessionId: str
    algorithm: str
    threshold: Optional[float] = 0.5


@app.post("/concept/update-mastery")
async def update_concept_mastery(request: UpdateMasteryRequest):
    """Update mastery score for a concept"""
    try:
        tracker = get_concept_tracker()
        score = tracker.calculate_mastery(
            request.sessionId,
            request.algorithm,
            request.concept,
            request.performanceData
        )
        
        return {
            "concept": request.concept,
            "newScore": score,
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/concept/weak-areas")
async def get_weak_areas(request: WeakAreasRequest):
    """Get weak concepts that need focus"""
    try:
        tracker = get_concept_tracker()
        weak = tracker.get_weak_concepts(
            request.sessionId,
            request.algorithm,
            request.threshold
        )
        
        focus = tracker.recommend_focus_areas(
            request.sessionId,
            request.algorithm,
            max_areas=3
        )
        
        return {
            "weakConcepts": weak,
            "recommendedFocus": focus
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# BATCH AI ANALYSIS ENDPOINT (Phase 4)
# ============================================

class BatchAnalysisRequest(BaseModel):
    sessionId: Optional[str] = None
    code: str
    array: List[int]


@app.post("/code/analyze-batch")
async def analyze_code_batch(request: BatchAnalysisRequest):
    """
    ONE comprehensive AI call to analyze code and generate everything.
    Returns: algorithm info, full trace, all explanations (3 modes), edge cases, questions
    
    This is 70% more token-efficient than per-step AI calls.
    """
    try:
        analyzer = get_batch_analyzer()
        
        # ONE AI call for everything
        analysis = await analyzer.comprehensive_analysis(
            code=request.code,
            array=request.array,
            session_id=request.sessionId
        )
        
        return {
            "success": True,
            "analysis": analysis,
            "cached": analysis.get("cache_key") in analyzer.cache,
            "tokenEstimate": analysis.get("token_estimate", 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================
# PRESET MANAGEMENT ENDPOINTS (Phase 3)
# ============================================

@app.get("/presets")
async def list_presets():
    """Get all available code presets"""
    try:
        preset_mgr = get_preset_manager()
        presets = preset_mgr.list_presets()
        return {
            "presets": presets,
            "count": len(presets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preset/{preset_id}")
async def get_preset(preset_id: str):
    """Get a specific preset's code"""
    try:
        preset_mgr = get_preset_manager()
        preset = preset_mgr.get_preset(preset_id)
        
        if not preset:
            raise HTTPException(status_code=404, detail=f"Preset '{preset_id}' not found")
        
        return preset
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
