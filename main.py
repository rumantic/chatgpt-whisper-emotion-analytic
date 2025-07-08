from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
import os
import aiofiles
import httpx
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

app = FastAPI()

# Настройки
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY = os.getenv("HTTP_PROXY")

# Интерфейс
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def upload_form(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

@app.post("/transcribe", response_class=HTMLResponse)
async def transcribe_audio(
    request: Request,
    file: UploadFile = File(None),
    text_input: str = Form(None),
    analyze: bool = Form(False)
):
    transcript = ""
    verdict = ""

    try:
        async with httpx.AsyncClient(proxies=PROXY, timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

            if file:
                if file.content_type not in ["audio/mpeg", "audio/wav"]:
                    return templates.TemplateResponse("upload.html", {"request": request, "error": "Формат файла не поддерживается."})

                # Сохраняем временный файл
                temp_filename = f"temp_{file.filename}"
                async with aiofiles.open(temp_filename, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)

                with open(temp_filename, 'rb') as f:
                    files = {"file": (file.filename, f, file.content_type)}
                    data = {"model": "whisper-1", "language": "ru"}
                    response = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, data=data, files=files)

                result = response.json()
                transcript = result.get("text", "Результат не получен")

                os.remove(temp_filename)

            elif text_input:
                transcript = text_input.strip()

            else:
                return templates.TemplateResponse("upload.html", {"request": request, "error": "Необходимо либо загрузить аудиофайл, либо ввести текст."})

            if analyze:
                emotion_prompt = (
                    "Проанализируй следующий текст звонка клиента в техническую поддержку и оцени, звучит ли он раздражённо, недовольно или агрессивно. "
                    "Выведи краткий вердикт: Спокойный / Недовольный / Агрессивный. Текст звонка: " + transcript
                )

                chat_response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json={
                        "model": "gpt-4",
                        "messages": [
                            {"role": "user", "content": emotion_prompt}
                        ]
                    }
                )

                emotion_result = chat_response.json()
                verdict = emotion_result['choices'][0]['message']['content'].strip()

    except Exception as e:
        transcript = f"Ошибка: {str(e)}"
        verdict = "Не удалось определить эмоциональную окраску"

    return templates.TemplateResponse("result.html", {"request": request, "transcript": transcript, "verdict": verdict, "analyze": analyze})
