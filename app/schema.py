from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# acount creation
class AccountBase(BaseModel):
    business_name: str
    email: EmailStr
    account_tier: str
    
class CreateAccount(AccountBase):
    password: str = Field(..., min_length=4, max_length=72)
    
class AccountCreated(AccountBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
 
# users

class AllUsers(AccountCreated):
    role: str
 
# user
class UserDetails(BaseModel):
    user: AccountCreated
    tickets: list[TicketResponse]
    
    class Config:
        from_attributes = True
    
# user login    
class Login(BaseModel):
    email: EmailStr
    password: str
    
class LoginResponse(BaseModel):
    token: str
    token_type: str
    user: AccountCreated
    
# admin 
class AdminBase(BaseModel):
    name: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminResponse(AdminBase):
    id: int
    role: str

    class Config:
        from_attributes = True
        
class AdminLoginResponse(BaseModel):
    token: str
    token_type: str
    user: AdminResponse
    
    
class TokenData(BaseModel):
    id: int | None = None

# ticket creation
class CreateTicketRequest(BaseModel):
    subject: str
    body: str
    type: str
    
class TicketResponse(BaseModel):
    id: int
    user_id: int
    subject: str
    body: str
    department: str
    confidence: float
    priority: str
    tags: list[str]
    extracted_keywords: list[str]
    status: str
    latency: float

# the model
class MetricsResponse(BaseModel):
    total_tickets: int
    avg_confidence: float
    avg_response_time_ms: float
    model_version: str
    routing_distribution: dict[str, int]
    

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    vectorizer_loaded: bool
    version: str

# department  
class DepartmentResponse(BaseModel):
    departments: list[str]
  
