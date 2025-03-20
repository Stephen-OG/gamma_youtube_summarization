from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from ..utils import user_serializer,video_serializer
from ..config.config import collection
from ..models.youtube import Video

router = APIRouter()

# Create Video
@router.post("/videos/")
async def create_user(video: Video):
    new_video = await collection["videos"].insert_one(video.model_dump())
    created_video = await collection["videos"].find_one({"_id": new_video.inserted_id})
    return video_serializer(created_video)

# Read All Videos
@router.get("/videos/")
async def get_users():
    videos = await collection["videos"].find().to_list(100)
    return [video_serializer(video) for video in videos]

# # Read Video by ID
# @router.get("/users/{user_id}")
# async def get_user(user_id: str):
#     user = await collection["users"].find_one({"_id": ObjectId(user_id)})
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return video_serializer(user)

# Update Video
@router.put("/videos/{video_id}")
async def update_user(video_id: str, video: Video):
    updated_video = await collection["users"].find_one_and_update(
        {"_id": ObjectId(video_id)},
        {"$set": video.model_dump()},
        return_document=True,
    )
    if not updated_video:
        raise HTTPException(status_code=404, detail="User not found")
    return video_serializer(updated_video)

# Delete Video
@router.delete("/video/{video_id}")
async def delete_user(video_id: str):
    result = await collection["videos"].delete_one({"_id": ObjectId(video_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
