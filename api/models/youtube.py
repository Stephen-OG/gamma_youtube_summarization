from pydantic import BaseModel

class Video(BaseModel):
    title: str
    video_url: str
    summary: str
    sentiment: str
    characters: str

class Transcript(BaseModel):
    transcript: str

class QueryParam(BaseModel):
    title: str