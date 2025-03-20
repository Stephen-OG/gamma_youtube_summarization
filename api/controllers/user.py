from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from ..utils import user_serializer
from ..config.config import collection
from ..models.user import User,UserLogin

router = APIRouter()

@router.post("/login")
async def login(user: UserLogin):
    user_exist = await collection["users"].find_one({"username": user.username})
    if not user_exist or user_exist["password"] != user.password:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"msg": "Login successful", "user": user_serializer(user_exist)}

# Create User
@router.post("/users/")
async def create_user(user: User):
    new_user = await collection["users"].insert_one(user.model_dump())
    created_user = await collection["users"].find_one({"_id": new_user.inserted_id})
    return user_serializer(created_user)

# Read All Users
@router.get("/users/")
async def get_users():
    users = await collection["users"].find().to_list(100)
    return [user_serializer(user) for user in users]

# Read User by ID
@router.get("/users/{user_id}")
async def get_user(user_id: str):
    user = await collection["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_serializer(user)

# Update User
@router.put("/users/{user_id}")
async def update_user(user_id: str, user: User):
    updated_user = await collection["users"].find_one_and_update(
        {"_id": ObjectId(user_id)},
        {"$set": user.model_dump()},
        return_document=True,
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_serializer(updated_user)

# Delete User
@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    result = await collection["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
