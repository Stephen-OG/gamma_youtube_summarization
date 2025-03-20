import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

def run_in_executor(func, *args):
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(executor, func, *args)

# Helper Function to Convert MongoDB Document
def user_serializer(user) -> dict:
    return {"id": str(user["_id"]), "name": user["name"], 
            "email": user["email"],"username": user["username"]}


def video_serializer(video) -> dict:
    return {"id": str(video["_id"]), "title": video["title"], "video_url": 
            video["video_url"], "summary": video["summary"], "sentiment":
              video["sentiment"], "characters": video["characters"]}

def video_summary(video) -> dict:
    return {"id": str(video["_id"]), "title": video["title"], "video_url": 
            video["video_url"], "summary": video["summary"]}


def create_character_prompt(character: dict, user_message: str) -> str:
        prompt_template = (
            "You are {name}, {personality}. "
            "Your description: {description}. "
            "Respond to the user in a way that reflects your personality. "
            "User: {user_message}"
        )
        return prompt_template.format(
            name=character["name"],
            personality=character["personality"],
            description=character["description"],
            user_message=user_message
        )
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_youtube_video",
            "description": "Search for a YouTube video based on a query.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The search title (e.g., 'Love in Every Word Omoni Oboli')."
                    },
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extract_transcript",
            "description": "Extract the transcript of a YouTube video.",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "The YouTube video ID."
                    }
                },
                "required": ["video_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_summary",
            "description": "Generate a summary of the transcript.",
            "parameters": {
                "type": "object",
                "properties": {
                    "transcript": {
                        "type": "string",
                        "description": "The video transcript."
                    }
                },
                "required": ["transcript"]
            }
        }
    }
]