import os
import random
import json
import numpy as np
import time
import asyncio
from typing import Tuple
from google import genai
from google.genai import errors, types
from dotenv import load_dotenv

max_retries = 3
API_TIMEOUT_SECONDS = 20
MAX_BACKOFF = 60
load_dotenv()

API_KEY = os.environ.get("GEMINI_API_KEY")
CLIENT = genai.Client(api_key=API_KEY) if API_KEY else None
_USED_HIDDEN_WORDS = set()

async def safe_generate_content(model, contents, config, timeout=20):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                CLIENT.models.generate_content,
                model=model,
                contents=contents,
                config=config,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise TimeoutError("API call timed out")

async def safe_embed_content(model, contents, timeout=20):
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                CLIENT.models.embed_content,
                model=model,
                contents=contents,
            ),
            timeout=timeout,
        )
    except asyncio.TimeoutError:
        raise TimeoutError("Embedding API call timed out")

def generate_topic_hidden_word()->str:
    file = open("./data/Namesle.json","r")
    name_list=json.load(file)
    name=random.choice(name_list).upper()
    print(f"{name}")
    time.sleep(2.8)
    return name


async def get_hint(player_word: str, hidden_word: str) -> Tuple[str, float]:
    if not CLIENT:
        #print("No API key. Returning fallback data.")
        return "LOCAL_HINT", 0.0

    validation_hint_system = (
        "You are generating hints for a name-guessing game. "
        "Generate one creative hint phrase related to BOTH the Player Word and the Hidden Word. "
        "Do NOT repeat the Player Word or the Hidden Word. "
        "The hint must be a phrase of one to three English words. "
        "Output JSON {\"hint_word\": \"...\"}."
    )

    validation_hint_query = (
        f"Hidden Word: {hidden_word}. Player Word: {player_word}. Provide one new hint phrase (up to 5 words)."
    )

    validation_hint_config = types.GenerateContentConfig(
        system_instruction=validation_hint_system,
        response_mime_type="application/json",
        response_schema=types.Schema(
            type=types.Type.OBJECT,
            properties={"hint_word": types.Schema(type=types.Type.STRING, nullable=True)},
        ),
        temperature=0.9
    )

    backoff = 1
    while True:
        try:
            response = await safe_generate_content(
                "gemini-2.5-flash",
                validation_hint_query,
                validation_hint_config,
                timeout=API_TIMEOUT_SECONDS,
            )
            parsed_json = json.loads(response.text)
            hint_raw = parsed_json.get("hint_word", "").strip().upper()

            if not hint_raw or hint_raw in ("NO HINT FOUND", player_word.upper(), hidden_word.upper()):
                print("Invalid hint.")
                return "No hint", 1

            if player_word.upper() in hint_raw or hidden_word.upper() in hint_raw:
                print("Hint contains player/hidden word.")
                return "No hint", 1
                
            if len(hint_raw.split()) > 5:
                print("Hint exceeded 5-word limit.")
                return "No hint", 1


            #print(f"Hint generated: {hint_raw}")
            hint = hint_raw
            break
        except errors.APIError as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"Model overloaded. Waiting {backoff}s before retry...")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
                continue
            else:
                print(f"Other API error: {e}")
                return "API Error", 0.0
        except TimeoutError:
            print(f"Timeout, retrying after {backoff}s...")
            await asyncio.sleep(backoff)
            backoff = min(backoff * 2, MAX_BACKOFF)
        except Exception as e:
            print(f"Hint generation failed: {e}")
            return "API Error", 0.0

    for attempt in range(max_retries):
        try:
            embedding_response = await safe_embed_content(
                "text-embedding-004",
                [player_word, hidden_word],
                timeout=API_TIMEOUT_SECONDS,
            )
            embeddings = embedding_response.embeddings
            if len(embeddings) < 2:
                raise ValueError("Embedding response invalid.")

            vec_player = np.array(embeddings[0].values)
            vec_hidden = np.array(embeddings[1].values)
            
            closeness = np.dot(vec_player, vec_hidden) / (
                np.linalg.norm(vec_player) * np.linalg.norm(vec_hidden)
            )
            return hint, float(closeness)
        except Exception as e:
            print(f"Embedding error: {e}. Default closeness = 0.")
            await asyncio.sleep(1)

    return hint, 0.0
