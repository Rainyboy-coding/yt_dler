from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import yt_dlp
import os
import time
from datetime import datetime
import asyncio
import json
import logging
import ssl
import certifi
import subprocess
import re

# 在文件开头添加日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 在 app = FastAPI() 之前添加
ssl._create_default_https_context = ssl._create_unverified_context

app = FastAPI()

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 确保下载目录存在
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 存储下载进度的字典
download_progress = {}
convert_progress = {}  # 新增转换进度字典

# 在存储下载进度的字典之后添加
NOTES_FILE = "notes.json"
notes = {}

# 启动时加载已有笔记
if os.path.exists(NOTES_FILE):
    with open(NOTES_FILE, 'r') as f:
        notes = json.load(f)

def download_video(url: str, video_id: str):
    try:
        def progress_hook(d):
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                downloaded = d.get('downloaded_bytes', 0)
                if total > 0:
                    progress = (downloaded / total) * 100
                    download_progress[video_id] = {
                        'progress': progress,
                        'status': 'downloading'
                    }
                    logger.info(f"Download progress: {progress:.2f}%")
            elif d['status'] == 'finished':
                download_progress[video_id]['status'] = 'finished'
                logger.info("Download finished")

        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]',
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_color': True,
            'extract_flat': False,
            'force_generic_extractor': False,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }, {
                'key': 'FFmpegEmbedSubtitle'
            }],
            'merge_output_format': 'mp4',
            'keepvideo': False,
            'keepaudio': False,
        }
        
        logger.info(f"Starting download for URL: {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # 先尝试获取视频信息
                info = ydl.extract_info(url, download=False)
                if info:
                    logger.info(f"Video info extracted: {info.get('title', 'Unknown')}")
                    # 如果信息获取成功，再进行下载
                    info = ydl.extract_info(url, download=True)
                    logger.info(f"Download completed for: {info.get('title', 'Unknown')}")
                    return info
                else:
                    raise Exception("无法获取视频信息")
            except Exception as e:
                logger.error(f"Download failed: {str(e)}")
                raise

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in download_video: {error_msg}")
        download_progress[video_id] = {
            'progress': 0,
            'status': 'error',
            'error': error_msg
        }
        raise

@app.get("/")
async def read_root(request: Request):
    # 获取已下载的视频列表
    videos = []
    for filename in os.listdir(DOWNLOAD_DIR):
        # 只显示合成后的 .mp4 文件
        if filename.endswith('.mp4'):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            file_stats = os.stat(file_path)
            videos.append({
                'title': filename,
                'path': f'/downloads/{filename}',
                'size': f'{file_stats.st_size / (1024*1024):.2f} MB',
                'date': datetime.fromtimestamp(file_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "videos": videos
    })

@app.post("/download")
async def download(background_tasks: BackgroundTasks, url: str = Form(...)):
    try:
        logger.info(f"Received download request for URL: {url}")
        video_id = str(time.time())
        download_progress[video_id] = {'progress': 0, 'status': 'starting'}
        
        # 在后台任务中下载视频
        background_tasks.add_task(download_video, url, video_id)
        
        return {"video_id": video_id}
    except Exception as e:
        logger.error(f"Error in download endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"下载失败: {str(e)}"}
        )

@app.get("/progress/{video_id}")
async def get_progress(video_id: str):
    return download_progress.get(video_id, {'progress': 0, 'status': 'unknown'})

@app.post("/delete")
async def delete_video(video_path: str = Form(...)):
    try:
        # 将 URL 路径转换为文件系统路径
        file_path = video_path.replace('/downloads/', f'{DOWNLOAD_DIR}/')
        
        # 删除视频文件
        os.remove(file_path)
        logger.info(f"Deleted video: {file_path}")
        return JSONResponse(
            status_code=200,
            content={"message": "视频已删除"}
        )
    except Exception as e:
        logger.error(f"Error deleting video: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"message": f"删除失败: {str(e)}"}
        )

# 配置视频文件的静态服务
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")

def convert_video(input_path: str, task_id: str):
    try:
        output_path = os.path.splitext(input_path)[0] + "_converted.mp4"
        cmd = [
            'ffmpeg',
            '-i', input_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental',
            '-y',  # 覆盖输出文件
            output_path
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )

        duration = None
        for line in process.stdout:
            if 'Duration' in line:
                duration = re.search(r'Duration: (\d+:\d+:\d+\.\d+)', line).group(1)
            elif 'time=' in line:
                time_match = re.search(r'time=(\d+:\d+:\d+\.\d+)', line)
                if time_match and duration:
                    current_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(time_match.group(1).split(':'))))
                    total_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(duration.split(':'))))
                    progress = (current_time / total_time) * 100
                    convert_progress[task_id] = {
                        'progress': progress,
                        'status': 'converting'
                    }

        process.wait()
        if process.returncode == 0:
            convert_progress[task_id]['status'] = 'completed'
            os.remove(input_path)  # 删除原始文件
            os.rename(output_path, input_path)  # 重命名转换后的文件
        else:
            raise Exception("视频转换失败")

    except Exception as e:
        logger.error(f"转换错误: {str(e)}")
        convert_progress[task_id] = {
            'progress': 0,
            'status': 'error',
            'error': str(e)
        }

@app.post("/convert")
async def convert(background_tasks: BackgroundTasks, video_path: str = Form(...)):
    try:
        task_id = str(time.time())
        file_path = video_path.replace('/downloads/', f'{DOWNLOAD_DIR}/')
        convert_progress[task_id] = {'progress': 0, 'status': 'starting'}
        
        background_tasks.add_task(convert_video, file_path, task_id)
        return {"task_id": task_id}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"转换失败: {str(e)}"}
        )

@app.get("/convert-progress/{task_id}")
async def get_convert_progress(task_id: str):
    return convert_progress.get(task_id, {'progress': 0, 'status': 'unknown'})

@app.post("/save-note")
async def save_note(content: str = Form(...)):
    try:
        note_id = str(time.time())
        notes[note_id] = {
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        # 保存到文件
        with open(NOTES_FILE, 'w') as f:
            json.dump(notes, f)
        return JSONResponse(
            status_code=200,
            content={"message": "保存成功"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"保存失败: {str(e)}"}
        )

@app.get("/get-notes")
async def get_notes():
    return notes

@app.delete("/delete-note/{note_id}")
async def delete_note(note_id: str):
    try:
        if note_id in notes:
            del notes[note_id]
            with open(NOTES_FILE, 'w') as f:
                json.dump(notes, f)
            return JSONResponse(
                status_code=200,
                content={"message": "删除成功"}
            )
        return JSONResponse(
            status_code=404,
            content={"message": "笔记不存在"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"删除失败: {str(e)}"}
        )

@app.put("/edit-note/{note_id}")
async def edit_note(note_id: str, content: str = Form(...)):
    try:
        if note_id in notes:
            notes[note_id]['content'] = content
            notes[note_id]['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            with open(NOTES_FILE, 'w') as f:
                json.dump(notes, f)
            return JSONResponse(
                status_code=200,
                content={"message": "修改成功"}
            )
        return JSONResponse(
            status_code=404,
            content={"message": "笔记不存在"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"修改失败: {str(e)}"}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8081,
        reload=True
    ) 