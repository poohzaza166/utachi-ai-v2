from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

class User(BaseModel):
    username: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def tokendecoding(token):
    return True

def get_current_user(token: str = Depends(oauth2_scheme)):
    user = tokendecoding(token)  # Replace with real token decoding
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user

