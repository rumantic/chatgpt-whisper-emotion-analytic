````markdown
# 🎧 Whisper Audio Web App

A simple web application built with FastAPI that allows users to:
- Upload `.mp3` or `.wav` audio files for transcription via OpenAI Whisper API.
- Optionally analyze the **emotional tone** of the conversation using OpenAI GPT-4.
- Alternatively, manually input text for emotion analysis.

## 🌍 Multilingual Interface
- 🇷🇺 Russian UI and language detection support.
- ✅ Emotion verdict in plain text: Calm / Dissatisfied / Aggressive.

---

## 🚀 Features

- 🎙️ Audio-to-text transcription (MP3/WAV).
- 💬 Text sentiment classification using GPT-4.
- 🌐 Proxy support via `.env`.
- 📦 Easy deployment with environment configuration.
- 🧪 Supports both file uploads and text input.

---

## 🔧 Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-name/whisper-audio-webapp.git
cd whisper-audio-webapp
````

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Then fill in your OpenAI API key and proxy if needed:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxx
HTTP_PROXY=http://localhost:8080
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
uvicorn main:app --reload
```

Then open in your browser: `http://localhost:8000`

---

## 📁 File structure

```
.
├── main.py
├── templates/
│   ├── upload.html
│   └── result.html
├── static/
├── .env
├── .env.example
└── requirements.txt
```

---

## 📃 License

MIT License — Free for personal or commercial use.

---

## 🇷🇺 Описание на русском

### 🎧 Веб-приложение на FastAPI

Этот сервис позволяет:

* Загружать `.mp3` или `.wav` файлы для распознавания речи через OpenAI Whisper.
* Опционально проводить **эмоциональный анализ** разговора через GPT-4.
* Альтернативно — вводить текст вручную для анализа.

### ⚙️ Возможности

* Распознавание речи на русском языке.
* Оценка эмоционального фона: Спокойный / Недовольный / Агрессивный.
* Поддержка прокси через `.env`.
* Интерфейс на русском языке.

### 📦 Установка

1. Клонируйте репозиторий и перейдите в папку проекта:

```bash
git clone https://github.com/your-name/whisper-audio-webapp.git
cd whisper-audio-webapp
```

2. Скопируйте файл настроек:

```bash
cp .env.example .env
```

3. Установите зависимости:

```bash
pip install -r requirements.txt
```

4. Запустите сервер:

```bash
uvicorn main:app --reload
```

И откройте `http://localhost:8000` в браузере.

