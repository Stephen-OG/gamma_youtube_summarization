from fastapi import APIRouter, HTTPException

from api.models.youtube import QueryParam, Transcript
from ..config.config import collection
from dotenv import load_dotenv
from ..services.summarize import extract_transcript, generate_summary, search_youtube_video
load_dotenv()

router = APIRouter(prefix='/api')

@router.post("/summarize")
async def summary(query: QueryParam):
    # Step 3: Generate the summary
    summary = await generate_summary(query.title)
    return summary

# @router.get("/ai/{title}")
# async def summarize(title: str):
#     try :
#         video = await search_youtube_video(title)
#         print(video)
#         return video

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/extract/{video_id}")
# async def summarize(video_id: str):
#     try :
#         transcript = await extract_transcript(video_id)
#         print(transcript)
#         return transcript

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.post("/summarize")
# async def summarize(transcript: Transcript):
#     try :
#         summary = generate_summary(transcript)
#         print(summary)
#         return summary

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
