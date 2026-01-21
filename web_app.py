import asyncio
import os
import uuid
from pathlib import Path
from typing import Dict, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from scribify.api_client import OpenAITranscriptionClient
from scribify.config import Config
from scribify.transcriber import Transcriber

app = FastAPI(title="Scribify API", version="1.0.0")

UPLOAD_DIR = Path("/tmp/scribify-uploads")
RESULTS_DIR = Path("/tmp/scribify-results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

transcription_jobs: Dict[str, Dict] = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scribify - Audio Transcription</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }

            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 600px;
                width: 100%;
            }

            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 28px;
            }

            .subtitle {
                color: #666;
                margin-bottom: 30px;
                font-size: 14px;
            }

            .upload-area {
                border: 2px dashed #667eea;
                border-radius: 10px;
                padding: 40px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-bottom: 20px;
            }

            .upload-area:hover {
                border-color: #764ba2;
                background: #f8f9ff;
            }

            .upload-area.dragover {
                border-color: #764ba2;
                background: #f0f3ff;
            }

            input[type="file"] {
                display: none;
            }

            .file-info {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9ff;
                border-radius: 8px;
                font-size: 14px;
                color: #555;
            }

            button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                width: 100%;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            button:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
            }

            button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .status {
                margin-top: 20px;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
            }

            .status.processing {
                background: #fff3cd;
                border: 1px solid #ffc107;
                color: #856404;
            }

            .status.success {
                background: #d4edda;
                border: 1px solid #28a745;
                color: #155724;
            }

            .status.error {
                background: #f8d7da;
                border: 1px solid #dc3545;
                color: #721c24;
            }

            .result {
                margin-top: 20px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                max-height: 300px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 13px;
                line-height: 1.6;
            }

            .spinner {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            .download-btn {
                margin-top: 15px;
                background: #28a745;
            }

            .upload-icon {
                font-size: 48px;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Scribify</h1>
            <p class="subtitle">Upload your audio file to get it transcribed using OpenAI's Whisper model</p>

            <div class="upload-area" id="uploadArea">
                <div class="upload-icon">📁</div>
                <div>
                    <strong>Click to upload</strong> or drag and drop<br>
                    <small>Supported formats: MP3, WAV, M4A, AAC, FLAC, OGG, WMA</small>
                </div>
                <input type="file" id="fileInput" accept="audio/*">
            </div>

            <div id="fileInfo" class="file-info" style="display: none;"></div>

            <button id="uploadBtn" disabled>Upload & Transcribe</button>

            <div id="status" style="display: none;"></div>
            <div id="result" class="result" style="display: none;"></div>
        </div>

        <script>
            const uploadArea = document.getElementById('uploadArea');
            const fileInput = document.getElementById('fileInput');
            const fileInfo = document.getElementById('fileInfo');
            const uploadBtn = document.getElementById('uploadBtn');
            const status = document.getElementById('status');
            const result = document.getElementById('result');

            let selectedFile = null;
            let currentJobId = null;

            uploadArea.addEventListener('click', () => fileInput.click());

            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('dragover');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('dragover');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('dragover');

                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    handleFileSelect(files[0]);
                }
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                }
            });

            function handleFileSelect(file) {
                selectedFile = file;
                fileInfo.textContent = `Selected: ${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
                fileInfo.style.display = 'block';
                uploadBtn.disabled = false;
                status.style.display = 'none';
                result.style.display = 'none';
            }

            uploadBtn.addEventListener('click', async () => {
                if (!selectedFile) return;

                uploadBtn.disabled = true;
                status.className = 'status processing';
                status.style.display = 'block';
                status.innerHTML = '<div class="spinner"></div><div>Uploading and transcribing...</div>';
                result.style.display = 'none';

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const response = await fetch('/transcribe', {
                        method: 'POST',
                        body: formData
                    });

                    if (!response.ok) {
                        throw new Error(`Upload failed: ${response.statusText}`);
                    }

                    const data = await response.json();
                    currentJobId = data.job_id;

                    pollJobStatus(currentJobId);
                } catch (error) {
                    status.className = 'status error';
                    status.innerHTML = `❌ Error: ${error.message}`;
                    uploadBtn.disabled = false;
                }
            });

            async function pollJobStatus(jobId) {
                try {
                    const response = await fetch(`/status/${jobId}`);
                    const data = await response.json();

                    if (data.status === 'completed') {
                        status.className = 'status success';
                        status.innerHTML = '✅ Transcription completed!';
                        result.style.display = 'block';
                        result.textContent = data.result;

                        const downloadBtn = document.createElement('button');
                        downloadBtn.className = 'download-btn';
                        downloadBtn.textContent = '📥 Download Transcript';
                        downloadBtn.onclick = () => {
                            const blob = new Blob([data.result], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = 'transcript.txt';
                            a.click();
                            URL.revokeObjectURL(url);
                        };

                        if (!document.querySelector('.download-btn')) {
                            result.parentElement.insertBefore(downloadBtn, result.nextSibling);
                        }

                        uploadBtn.disabled = false;
                    } else if (data.status === 'failed') {
                        status.className = 'status error';
                        status.innerHTML = `❌ Transcription failed: ${data.error}`;
                        uploadBtn.disabled = false;
                    } else {
                        setTimeout(() => pollJobStatus(jobId), 2000);
                    }
                } catch (error) {
                    status.className = 'status error';
                    status.innerHTML = `❌ Error checking status: ${error.message}`;
                    uploadBtn.disabled = false;
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Upload an audio file and start transcription"""
    job_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / f"{job_id}_{file.filename}"

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        transcription_jobs[job_id] = {
            "status": "processing",
            "file_path": str(file_path),
            "result": None,
            "error": None,
        }

        asyncio.create_task(process_transcription(job_id, str(file_path)))

        return JSONResponse(
            content={
                "job_id": job_id,
                "status": "processing",
                "message": "Transcription job started",
            }
        )
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(status_code=500, detail=str(e))


async def process_transcription(job_id: str, file_path: str):
    """Background task to process transcription"""
    try:
        config = Config.load()
        client = OpenAITranscriptionClient(
            api_key=config.api_key, model=config.model
        )
        transcriber = Transcriber(client=client, quiet=True)

        result = await asyncio.to_thread(transcriber.transcribe, file_path)

        transcription_jobs[job_id]["status"] = "completed"
        transcription_jobs[job_id]["result"] = result

        result_path = RESULTS_DIR / f"{job_id}.txt"
        with open(result_path, "w") as f:
            f.write(result)

    except Exception as e:
        transcription_jobs[job_id]["status"] = "failed"
        transcription_jobs[job_id]["error"] = str(e)
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass


@app.get("/status/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a transcription job"""
    if job_id not in transcription_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = transcription_jobs[job_id]
    return JSONResponse(
        content={
            "job_id": job_id,
            "status": job["status"],
            "result": job["result"],
            "error": job["error"],
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for Docker"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
