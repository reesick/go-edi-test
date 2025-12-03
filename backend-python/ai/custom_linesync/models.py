"""
Pydantic Models for LineSync AI

Strict validation models for Gemini API responses to ensure
production-grade reliability and type safety.
"""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, Field, validator, model_validator
from enum import Enum


class HighlightType(str, Enum):
    """Types of code line highlights"""
    COMPARISON = "comparison"
    MODIFICATION = "modification"
    ASSIGNMENT = "assignment"
    CONDITION = "condition"
    DEFAULT = "default"


class HighlightInfo(BaseModel):
    """Highlight information for array elements"""
    indices: List[int] = Field(default_factory=list, description="Indices to highlight")
    colors: List[str] = Field(default_factory=list, description="Colors for highlights")
    labels: List[str] = Field(default_factory=list, description="Labels for highlighted elements")
    
    @validator('indices', 'colors', 'labels')
    def list_must_not_be_too_large(cls, v):
        if len(v) > 100:
            raise ValueError('Highlight lists cannot exceed 100 elements')
        return v


class ArrayState(BaseModel):
    """State of an array at a given frame"""
    name: str = Field(..., min_length=1, max_length=50)
    values: List[Union[int, float, str]] = Field(..., max_items=1000)
    type: str = Field(..., description="Data type of array elements")
    highlights: Optional[HighlightInfo] = None
    sorted_region: Optional[List[int]] = None
    
    @validator('values')
    def values_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Array values cannot be empty')
        return v
    
    @validator('sorted_region')
    def sorted_region_must_be_valid(cls, v):
        if v is not None and len(v) != 2:
            raise ValueError('sorted_region must be [start, end] indices')
        return v


class VariableState(BaseModel):
    """State of a variable at a given frame"""
    name: str = Field(..., min_length=1, max_length=50)
    value: Union[int, float, str, bool] = Field(...)
    type: str = Field(..., description="Data type of variable")


class PointerState(BaseModel):
    """State of a pointer at a given frame"""
    name: str = Field(..., min_length=1, max_length=50)
    points_to_index: int = Field(..., ge=0)
    color: str = Field(default="blue")


class TreeNode(BaseModel):
    """Node in a tree structure"""
    id: int = Field(..., ge=0)
    value: Union[int, str, float] = Field(...)
    x: float = Field(..., ge=0, le=2000, description="X coordinate for rendering")
    y: float = Field(..., ge=0, le=2000, description="Y coordinate for rendering")
    left_child_id: Optional[int] = None
    right_child_id: Optional[int] = None
    color: str = Field(default="default")
    highlighted: bool = Field(default=False)


class TreeStructure(BaseModel):
    """Complete tree structure"""
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., description="Type of tree (binary, bst, heap, etc.)")
    nodes: List[TreeNode] = Field(..., max_items=1000)
    
    @validator('nodes')
    def nodes_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Tree must have at least one node')
        return v


class GraphNode(BaseModel):
    """Node in a graph"""
    id: int = Field(..., ge=0)
    label: str = Field(..., max_length=50)
    x: float = Field(..., ge=0, le=2000)
    y: float = Field(..., ge=0, le=2000)
    color: str = Field(default="default")
    highlighted: bool = Field(default=False)


class GraphEdge(BaseModel):
    """Edge in a graph"""
    from_node: int = Field(..., ge=0, alias="from")
    to_node: int = Field(..., ge=0, alias="to")
    weight: Optional[Union[int, float]] = None
    color: str = Field(default="default")
    highlighted: bool = Field(default=False)
    directed: bool = Field(default=True)
    
    class Config:
        populate_by_name = True


class GraphStructure(BaseModel):
    """Complete graph structure"""
    name: str = Field(..., min_length=1, max_length=50)
    type: str = Field(..., description="Type of graph (directed, undirected, weighted)")
    nodes: List[GraphNode] = Field(..., max_items=1000)
    edges: List[GraphEdge] = Field(default_factory=list, max_items=5000)
    
    @validator('nodes')
    def nodes_must_not_be_empty(cls, v):
        if len(v) == 0:
            raise ValueError('Graph must have at least one node')
        return v


class StackState(BaseModel):
    """State of a stack"""
    name: str = Field(..., min_length=1, max_length=50)
    values: List[Union[int, float, str]] = Field(default_factory=list, max_items=1000)
    highlights: Optional[HighlightInfo] = None


class QueueState(BaseModel):
    """State of a queue"""
    name: str = Field(..., min_length=1, max_length=50)
    values: List[Union[int, float, str]] = Field(default_factory=list, max_items=1000)
    front_index: int = Field(default=0, ge=0)
    rear_index: int = Field(default=0, ge=0)
    highlights: Optional[HighlightInfo] = None


class VisualizationFrame(BaseModel):
    """Single frame in the visualization"""
    frame_id: int = Field(..., ge=0)
    timestamp_ms: int = Field(default=0, ge=0)
    description: str = Field(..., min_length=1, max_length=500)
    
    # Data structures (all optional, empty arrays if not used)
    arrays: List[ArrayState] = Field(default_factory=list, max_items=20)
    variables: List[VariableState] = Field(default_factory=list, max_items=50)
    pointers: List[PointerState] = Field(default_factory=list, max_items=20)
    trees: List[TreeStructure] = Field(default_factory=list, max_items=10)
    graphs: List[GraphStructure] = Field(default_factory=list, max_items=10)
    stacks: List[StackState] = Field(default_factory=list, max_items=10)
    queues: List[QueueState] = Field(default_factory=list, max_items=10)
    
    @validator('frame_id')
    def frame_id_must_be_non_negative(cls, v):
        if v < 0:
            raise ValueError('frame_id must be non-negative')
        return v
    
    @model_validator(mode='after')
    def at_least_one_structure(self):
        """Ensure at least one data structure is present"""
        structures = ['arrays', 'variables', 'trees', 'graphs', 'stacks', 'queues']
        if not any(getattr(self, s) for s in structures):
            raise ValueError('Frame must contain at least one data structure or variable')
        return self


class LineSyncMapping(BaseModel):
    """Mapping of a frame to source code lines"""
    frame_id: int = Field(..., ge=0)
    line_numbers: List[int] = Field(..., min_items=1, max_items=20)
    code_snippet: str = Field(..., min_length=1, max_length=1000)
    explanation: str = Field(..., min_length=1, max_length=500)
    highlight_type: HighlightType = Field(default=HighlightType.DEFAULT)
    
    @validator('line_numbers')
    def line_numbers_must_be_positive(cls, v):
        if any(line < 1 for line in v):
            raise ValueError('Line numbers must be positive (1-indexed)')
        if any(line > 100 for line in v):
            raise ValueError('Line numbers cannot exceed 100')
        return v


class LineSyncData(BaseModel):
    """Complete line synchronization data"""
    setup_lines: List[int] = Field(default_factory=list, max_items=50)
    frame_mappings: List[LineSyncMapping] = Field(..., min_items=1, max_items=500)
    non_visualized_lines: List[int] = Field(default_factory=list, max_items=100)
    
    @validator('setup_lines', 'non_visualized_lines')
    def line_numbers_valid(cls, v):
        if any(line < 1 or line > 100 for line in v):
            raise ValueError('Line numbers must be between 1 and 100')
        return v


class MetadataModel(BaseModel):
    """Metadata about the visualization"""
    total_frames: int = Field(..., ge=1, le=500)
    complexity: str = Field(..., description="Complexity level: low, medium, high")
    data_structures_used: List[str] = Field(..., min_items=1, max_items=20)
    
    @validator('complexity')
    def complexity_must_be_valid(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Complexity must be low, medium, or high')
        return v


class VisualizationData(BaseModel):
    """Complete visualization data"""
    frames: List[VisualizationFrame] = Field(..., min_items=1, max_items=500)
    
    @validator('frames')
    def frames_must_be_sequential(cls, v):
        """Ensure frame IDs are sequential starting from 0"""
        expected_ids = list(range(len(v)))
        actual_ids = [frame.frame_id for frame in v]
        if actual_ids != expected_ids:
            raise ValueError('Frame IDs must be sequential starting from 0')
        return v


class GeminiResponse(BaseModel):
    """Complete response from Gemini API"""
    metadata: MetadataModel = Field(...)
    visualization: VisualizationData = Field(...)
    linesync: LineSyncData = Field(...)
    
    @model_validator(mode='after')
    def validate_consistency(self):
        """Ensure frame mappings match visualization frames"""
        viz_data = self.visualization
        linesync_data = self.linesync
        
        if viz_data and linesync_data:
            viz_frame_ids = {frame.frame_id for frame in viz_data.frames}
            mapping_frame_ids = {mapping.frame_id for mapping in linesync_data.frame_mappings}
            
            # All linesync mappings must reference valid frames
            invalid_mappings = mapping_frame_ids - viz_frame_ids
            if invalid_mappings:
                raise ValueError(f'LineSyncMappings reference non-existent frames: {invalid_mappings}')
        
        return self


class FallbackVisualization(BaseModel):
    """Simplified visualization used when AI fails"""
    frames: List[Dict[str, Any]]
    error_message: str
    is_fallback: bool = True
