from typing import Optional
from pydantic import BaseModel

class CustomerBase(BaseModel):
  username: str
  email: str
  password: str
  url: str
  database: Optional[str] | None

class CustomerUpdate(BaseModel):
  username: Optional[str] | None
  email: Optional[str] | None
  password: Optional[str] | None
  url: Optional[str] | None
  database: Optional[str] | None

class CustomerResponse(BaseModel):
  id: str
  username: str
  email: str
  url: str
  class Config():
    from_attributes = True

class CustomerApiResponse(BaseModel):
  user_data: CustomerResponse
  webhook_url: str

class CustomerCheck(BaseModel):
  email: str
  password: str