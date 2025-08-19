from pydantic import BaseModel, Field
from typing import List, Optional

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float

class SourceLocation(BaseModel):
    page: int
    bbox: Optional[BoundingBox] = None

class ExtractedField(BaseModel):
    name: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Optional[SourceLocation] = None

class QualityAssurance(BaseModel):
    passed_rules: List[str] = []
    failed_rules: List[str] = []
    notes: str = ""

class ExtractionResult(BaseModel):
    doc_type: str
    fields: List[ExtractedField]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    qa: QualityAssurance
    processing_time: Optional[float] = None
