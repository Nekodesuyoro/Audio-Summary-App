from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import whisper
import tempfile
import os
import requests
import json
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print(f"[debug] Script location: {Path(__file__).parent}")
print(f"[debug] .env path: {env_path}")
print(f"[debug] .env exists: {env_path.exists()}")

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("[init] loading whisper model...")
model = whisper.load_model("medium")
print("[init] whisper model loaded.")


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
print(f"[init] API Key found: {bool(OPENROUTER_API_KEY)}")
if OPENROUTER_API_KEY:
    print(f"[init] API Key length: {len(OPENROUTER_API_KEY)}")
    print(f"[init] API Key starts with: {OPENROUTER_API_KEY[:15]}...")
else:
    print("[init] WARNING: No API Key found in environment variables!")
    print("[init] Please create a .env file with OPENROUTER_API_KEY=your-key")

@app.get("/")
def root():
    return {"message": "audio transcription server"}

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    print(f"[upload] {file.filename}")

    try:
        
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            raw = await file.read()
            tmp.write(raw)
            tmp_path = tmp.name

        print(f"[file] saved temp file: {tmp_path}")

        
        result = model.transcribe(tmp_path, language="ja")
        text = result.get("text", "").strip()
        print(f"[whisper] transcript length: {len(text)} chars")
        print(f"[whisper] transcript preview: {text[:100]}...")

        
        os.unlink(tmp_path)

        if not text:
            raise HTTPException(status_code=400, detail="音声の解析に失敗しました")

        summary = None
        points = []

        
        if OPENROUTER_API_KEY:
            print("[summary] API key found, requesting summary...")
            try:
                summary_data = request_summary(text)
                print(f"[summary] received: {summary_data}")
                summary = summary_data.get("summary")
                points = summary_data.get("key_points", [])
                print(f"[summary] summary length: {len(summary) if summary else 0}")
                print(f"[summary] key points count: {len(points)}")
            except Exception as e:
                print(f"[summary error] {type(e).__name__}: {e}")
        else:
            print("[summary] skipped: no API key found")

        return {
            "success": True,
            "transcription": text,
            "summary": summary,
            "key_points": points,
            "filename": file.filename,
        }

    except Exception as e:
        print(f"[error] {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def request_summary(text: str):
    """OpenRouter経由でDeepSeekを使って要約を取得"""
    

    prompt = f"""以下の文字起こしテキストを要約してください。

JSON形式で返してください：
{{
  "summary": "全体の要約を100文字程度で",
  "key_points": ["重要なポイント1", "重要なポイント2", "重要なポイント3"]
}}

テキスト:
{text}
"""

    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    print(f"[api] sending request to OpenRouter...")
    print(f"[api] text length: {len(text)} chars")
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"[api] status code: {response.status_code}")
        
        if response.status_code != 200:
            error_text = response.text
            print(f"[api error] {error_text}")
            raise Exception(f"API error {response.status_code}: {error_text}")

        response_json = response.json()
        print(f"[api] full response: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        
    
        content = response_json["choices"][0]["message"]["content"]
        print(f"[api] content: {content}")
        
        # JSONをパース
        cleaned = content.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
        
        print(f"[api] cleaned content: {cleaned}")

        try:
            parsed = json.loads(cleaned)
            return parsed
        except json.JSONDecodeError as e:
            print(f"[json error] Failed to parse: {e}")
            return {"summary": content, "key_points": []}
            
    except requests.exceptions.Timeout:
        print("[api error] Request timeout")
        raise Exception("API request timeout")
    except Exception as e:
        print(f"[api error] {type(e).__name__}: {e}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)