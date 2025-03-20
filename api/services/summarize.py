from groq import Groq
import json
from dotenv import load_dotenv
from ..utils import run_in_executor
import os
from serpapi import GoogleSearch
from youtube_transcript_api import YouTubeTranscriptApi
from groq import Groq
import asyncio

load_dotenv()

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

async def search_youtube_video(title):
    params = {
        'engine': "youtube",
        'search_query': title,
        'api_key': SERPAPI_API_KEY
    }
    search = GoogleSearch(params)

    # Run search in an async-compatible way
    results = await run_in_executor(search.get_dict)

    if "video_results" in results:
        video = results["video_results"][0]  # Get the first result
        return {
            "title": video["title"],
            "link": video["link"],
            "video_id": video["link"].split("v=")[-1]
        }
    return None

async def extract_transcript(video_id: str) -> str:
    try:
        # Fetch the transcript
        raw_transcript = await run_in_executor(lambda: YouTubeTranscriptApi.get_transcript(video_id))
        transcript = " ".join([entry["text"] for entry in raw_transcript])

        return transcript
    except Exception as e:
        raise ValueError(f"Failed to extract transcript: {e}")


async def generate_summary(title: str):
    messages = [
        {"role": "system", "content": "You are an AI that searches YouTube videos, extracts transcripts, and summarizes them."},
        {"role": "user", "content": title}
    ]

    try:
        response = await asyncio.to_thread(client.chat.completions.create,
            model='llama-3.3-70b-versatile',
            messages=messages,
            tools=tools,  
            tool_choice="auto",
        )

        print("response1", response)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls if hasattr(response_message, "tool_calls") else None

        if tool_calls:
            function_responses = []

            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                if function_name == "search_youtube_video":
                    video_info = await search_youtube_video(**function_args)
                    if not video_info:
                        return "No YouTube video found."

                    function_responses.append({
                        "tool_call_id": tool_call.id,  
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(video_info)
                    })

                    video_id = video_info["video_id"]
                    transcript = await extract_transcript(video_id)
                    if not transcript:
                        return "Transcript not available."

                    function_responses.append({
                        "tool_call_id": tool_call.id, 
                        "role": "tool",
                        "name": "extract_transcript",
                        "content": transcript 
                    })

                    # Run sentiment analysis and character identification **in parallel**
                    sentiment_task = asyncio.to_thread(analyze_sentiment, transcript)
                    characters_task = asyncio.to_thread(identify_characters, transcript)
                    sentiment, characters = await asyncio.gather(sentiment_task, characters_task)

                    function_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "analyze_sentiment_with_groq",
                        "content": sentiment
                    })

                    function_responses.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": "identify_characters_with_groq",
                        "content": json.dumps(characters)
                    })

            messages.extend(function_responses)

            second_response = await asyncio.to_thread(client.chat.completions.create,
                model='llama-3.3-70b-versatile',
                messages=messages,
                max_tokens=400
            )

            return second_response.choices[0].message.content

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Failed to generate summary."


def text_to_speech(summary: str) -> None:
    return


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
]
def analyze_sentiment(transcript: str) -> str:
    prompt = f"""
    Analyze the sentiment of the following text. 
    Return one of the following: "positive", "negative", or "neutral".

    Text:
    {transcript}
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes sentiment."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile"
    )
    sentiment = response.choices[0].message.content.strip()
    return sentiment


def identify_characters(transcript: str) -> list:
    prompt = f"""
    Identify the main characters mentioned in the following text. 
    Return a list of their names.

    Text:
    {transcript}
    """
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that identifies characters."},
            {"role": "user", "content": prompt}
        ],
        model="llama-3.3-70b-versatile"
    )
    characters = response.choices[0].message.content.strip().split(", ")
    return characters


# def generate_summary(title: str):
#     messages = [
#     {"role": "system", "content": "You are a helpful assistant that can search for YouTube videos and extract transcripts using available tools. Use the appropriate tool to find a video based on a given title, extract its transcript, and summarize it in under 400 words."},
#     {"role": "user", "content": title}
# ]

#     try:
#         response = client.chat.completions.create(
#             model='llama-3.3-70b-versatile',
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",
#             max_tokens=400,
#         )
#         print("response1", response)

#         response_message = response.choices[0].message
#         tool_calls = response_message.tool_calls
#         print(f"Initial Response: \n{response.choices[0].message}\n\n")

#         if tool_calls:
#             available_functions = {
#                 "search_youtube_video": search_youtube_video,
#                 "extract_transcript": extract_transcript
#             }
#             messages.append(response_message)

#             for tool_call in tool_calls:
#                 function_name = tool_call.function.name
#                 function_to_call = available_functions.get(function_name, None)
#                 function_args = json.loads(tool_call.function.arguments)
#                 function_response = function_to_call(**function_args)
#                 messages.append(
#                     {
#                         "tool_call_id": tool_call.id,
#                         "role": "tool",
#                         "name": function_name,
#                         "content": str(function_response)
#                     }
#                 )

#             second_response = client.chat.completions.create(
#                 model='llama-3.3-70b-versatile',
#                 messages = messages
#             )
#             response = second_response

#         return response.choices[0].message.content

#     except Exception as e:
#         raise ValueError(f"Failed to generate summary: {e}")

