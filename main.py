from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import openai
import os
import aiofiles
import httpx
from dotenv import load_dotenv
import logging
import time

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),  # Вывод в консоль
        logging.FileHandler("debug.log", encoding="utf-8")  # Логирование в файл
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Настройки
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROXY = os.getenv("HTTP_PROXY")

logger.info(f"OPENAI_API_KEY loaded: {'Yes' if OPENAI_API_KEY else 'No'}")
logger.info(f"HTTP_PROXY: {PROXY}")


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
        logger.info("Creating httpx.AsyncClient...")
        async with httpx.AsyncClient(proxies=PROXY, timeout=60.0) as client:
            headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
            logger.info(f"Headers set: {headers}")

            if file and file.filename:
                logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")
                if file.content_type not in ["audio/mpeg", "audio/wav"]:
                    logger.warning("Unsupported file format")
                    return templates.TemplateResponse("upload.html", {"request": request, "error": "Формат файла не поддерживается."})

                # Сохраняем временный файл в /tmp с временной меткой
                tmp_dir = os.path.join(os.getcwd(), "tmp")
                os.makedirs(tmp_dir, exist_ok=True)
                timestamp = int(time.time())
                temp_filename = os.path.join(tmp_dir, f"temp_{timestamp}_{file.filename}")
                logger.info(f"Saving temporary file: {temp_filename}")
                async with aiofiles.open(temp_filename, 'wb') as out_file:
                    content = await file.read()
                    await out_file.write(content)

                logger.info("Sending audio to OpenAI Whisper API...")
                with open(temp_filename, 'rb') as f:
                    files = {"file": (file.filename, f, file.content_type)}
                    data = {"model": "whisper-1", "language": "ru"}
                    response = await client.post("https://api.openai.com/v1/audio/transcriptions", headers=headers, data=data, files=files)
                logger.info(f"Whisper API response status: {response.status_code}")

                result = response.json()
                logger.info(f"Whisper API response: {result}")
                transcript = result.get("text", "Результат не получен")

                # Файл не удаляем, оставляем для истории
                logger.info(f"Temporary file {temp_filename} saved and kept for history.")

            elif text_input:
                logger.info("Text input provided.")
                transcript = text_input.strip()

            else:
                logger.warning("No file or text input provided.")
                return templates.TemplateResponse("upload.html", {"request": request, "error": "Необходимо либо загрузить аудиофайл, либо ввести текст."})

            if analyze:
                logger.info("Emotion analysis requested.")
                emotion_prompt = (
                    "Проанализируй следующий текст звонка клиента в техническую поддержку и оцени, звучит ли он раздражённо, недовольно или агрессивно. "
                    "Выведи краткий вердикт: Спокойный / Недовольный / Агрессивный. Текст звонка: " + transcript
                )

                logger.info("Sending prompt to OpenAI Chat API...")
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
                logger.info(f"Chat API response status: {chat_response.status_code}")

                emotion_result = chat_response.json()
                logger.info(f"Chat API response: {emotion_result}")
                verdict = emotion_result['choices'][0]['message']['content'].strip()

    except Exception as e:
        logger.exception("Exception occurred during transcription or analysis")
        transcript = f"Ошибка: {str(e)}"
        verdict = "Не удалось определить эмоциональную окраску"

    return templates.TemplateResponse("result.html", {"request": request, "transcript": transcript, "verdict": verdict, "analyze": analyze})
