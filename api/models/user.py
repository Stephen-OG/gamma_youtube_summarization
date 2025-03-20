from pydantic import BaseModel

class User(BaseModel):
    name: str
    email: str
    password: str
    username: str

# Model for user login
class UserLogin(BaseModel):
    username: str
    password: str