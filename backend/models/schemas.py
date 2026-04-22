from pydantic import BaseModel, EmailStr
from typing import Optional, Any, List, Dict

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    confirm_password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ChatRequest(BaseModel):
    query: str
    file_id: int
    conversation_history: List[Dict[str, Any]] = []

class AnalysisRequest(BaseModel):
    query: str
    file_id: int
    intent: Optional[str] = None

class PredictionRequest(BaseModel):
    file_id: int
    target_column: str
    models: List[str] = ["RandomForest", "GradientBoosting"]

class FileLoadRequest(BaseModel):
    file_id: int
