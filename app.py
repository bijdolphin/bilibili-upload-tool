#!/usr/bin/env python3
"""
YouTube to Bilibili Web Application
Upload YouTube videos to Bilibili with a simple web interface
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import asyncio
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
import queue

# Import our upload module
from bilibili_api import video_uploader, Credential

app = Flask(__name__)
CORS(app)

# Configuration
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)

# Your Bilibili credentials (from the working script)
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOFA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6"
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"

# Global progress tracking
progress_queue = queue.Queue()
current_task = {"status": "idle", "message": "", "progress": 0}

def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})',
        r'(?:youtu.be\/)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_youtube_video(url, progress_callback=None):
    """Download YouTube video using yt-dlp"""
    video_id = extract_video_id(url)
    if not video_id:
        raise ValueError("Invalid YouTube URL")
    
    output_path = VIDEOS_DIR / f"%(title)s-{video_id}.%(ext)s"
    
    # Progress tracking for yt-dlp
    if progress_callback:
        progress_callback("Starting YouTube download...", 10)
    
    cmd = [
        "yt-dlp",
        "-f", "best[ext=mp4]/best",
        "-o", str(output_path),
        "--no-playlist",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Find the downloaded file
        for file in VIDEOS_DIR.glob(f"*-{video_id}.mp4"):
            if progress_callback:
                progress_callback(f"Downloaded: {file.name}", 30)
            return str(file)
        
        # If mp4 not found, look for any video file
        for file in VIDEOS_DIR.glob(f"*-{video_id}.*"):
            if progress_callback:
                progress_callback(f"Downloaded: {file.name}", 30)
            return str(file)
            
    except subprocess.CalledProcessError as e:
        raise Exception(f"Download failed: {e.stderr}")
    
    raise Exception("Downloaded file not found")

def get_video_info(url):
    """Get video information from YouTube"""
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--no-playlist",
        url
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return {
            "title": info.get("title", "Unknown"),
            "description": info.get("description", ""),
            "duration": info.get("duration", 0),
            "uploader": info.get("uploader", "Unknown"),
            "upload_date": info.get("upload_date", ""),
            "view_count": info.get("view_count", 0),
            "thumbnail": info.get("thumbnail", "")
        }
    except:
        return None

async def upload_to_bilibili(video_path, title, desc, tags, progress_callback=None):
    """Upload video to Bilibili"""
    
    if progress_callback:
        progress_callback("Preparing Bilibili upload...", 40)
    
    # Check/create cover
    cover_file = Path("cover.jpg")
    if not cover_file.exists():
        # Create cover
        subprocess.run(["python", "create_cover.py"], check=True)
    
    try:
        # Create credential
        credential = Credential(
            sessdata=SESSDATA,
            bili_jct=BILI_JCT,
            buvid3=BUVID3
        )
        
        if progress_callback:
            progress_callback("Authenticated with Bilibili", 50)
        
        # Meta data
        meta = {
            "copyright": 2,  # 转载
            "source": "YouTube",
            "tid": 21,  # 日常分区
            "title": title[:80],  # Bilibili title limit
            "desc_format_id": 0,
            "desc": desc[:2000],  # Bilibili description limit
            "dynamic": "",
            "tags": tags[:10],  # Max 10 tags
        }
        
        # Create uploader
        video_file = Path(video_path).resolve()
        
        upload_args = {
            "pages": [
                video_uploader.VideoUploaderPage(
                    path=str(video_file),
                    title=title[:80],
                    description=""
                )
            ],
            "meta": meta,
            "credential": credential
        }
        
        if cover_file.exists():
            upload_args["cover"] = str(cover_file.resolve())
        
        uploader = video_uploader.VideoUploader(**upload_args)
        
        # Track upload progress
        @uploader.on("PRE_CHUNK")
        async def on_pre_chunk(data):
            if progress_callback:
                percent = 60 + (data["chunk_number"] / data["total_chunk_count"]) * 30
                progress_callback(f"Uploading: {data['chunk_number']}/{data['total_chunk_count']}", percent)
        
        @uploader.on("AFTER_CHUNK")
        async def on_after_chunk(data):
            if progress_callback:
                percent = 60 + ((data["chunk_number"] + 1) / data["total_chunk_count"]) * 30
                progress_callback(f"Uploading: {data['chunk_number'] + 1}/{data['total_chunk_count']}", percent)
        
        @uploader.on("PRE_SUBMIT")
        async def on_pre_submit(data):
            if progress_callback:
                progress_callback("Submitting to Bilibili...", 95)
        
        # Execute upload
        result = await uploader.start()
        
        if result:
            bvid = result.get('bvid')
            if progress_callback:
                progress_callback(f"Success! BV: {bvid}", 100)
            
            return {
                "success": True,
                "bvid": bvid,
                "url": f"https://www.bilibili.com/video/{bvid}"
            }
            
    except Exception as e:
        raise Exception(f"Upload failed: {str(e)}")

def process_video(youtube_url):
    """Main processing function"""
    global current_task
    
    def update_progress(message, progress):
        current_task["message"] = message
        current_task["progress"] = progress
        current_task["status"] = "processing"
        progress_queue.put(current_task.copy())
    
    try:
        # Get video info
        update_progress("Fetching video information...", 5)
        info = get_video_info(youtube_url)
        if not info:
            info = {"title": "Unknown Video", "description": ""}
        
        # Prepare Chinese metadata
        title = f"{info['title']} [搬运]"
        if len(title) > 80:
            title = title[:77] + "..."
        
        desc = f"""原视频：{youtube_url}
原作者：{info.get('uploader', 'Unknown')}
上传日期：{info.get('upload_date', 'Unknown')}

{info.get('description', '')[:1500]}"""
        
        tags = ["YouTube", "搬运", "视频", "分享", "国外视频"]
        
        # Download video
        update_progress("Downloading from YouTube...", 10)
        video_path = download_youtube_video(youtube_url, update_progress)
        
        # Upload to Bilibili
        update_progress("Uploading to Bilibili...", 40)
        
        # Run async upload in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            upload_to_bilibili(video_path, title, desc, tags, update_progress)
        )
        loop.close()
        
        current_task["status"] = "completed"
        current_task["result"] = result
        progress_queue.put(current_task.copy())
        
        return result
        
    except Exception as e:
        current_task["status"] = "error"
        current_task["message"] = str(e)
        current_task["progress"] = 0
        progress_queue.put(current_task.copy())
        raise

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle upload request"""
    global current_task
    
    data = request.json
    youtube_url = data.get('url', '').strip()
    
    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400
    
    if current_task["status"] == "processing":
        return jsonify({"error": "Another upload is in progress"}), 400
    
    # Reset task status
    current_task = {"status": "processing", "message": "Starting...", "progress": 0}
    
    # Start processing in background
    thread = threading.Thread(target=process_video, args=(youtube_url,))
    thread.daemon = True
    thread.start()
    
    return jsonify({"message": "Upload started", "status": "processing"})

@app.route('/api/progress')
def progress():
    """SSE endpoint for progress updates"""
    def generate():
        while True:
            try:
                # Get progress update with timeout
                update = progress_queue.get(timeout=1)
                yield f"data: {json.dumps(update)}\n\n"
                
                # If completed or error, stop sending updates
                if update["status"] in ["completed", "error"]:
                    break
                    
            except queue.Empty:
                # Send heartbeat
                yield f"data: {json.dumps(current_task)}\n\n"
            
            time.sleep(0.5)
    
    return Response(generate(), mimetype="text/event-stream")

@app.route('/api/status')
def status():
    """Get current status"""
    return jsonify(current_task)

if __name__ == '__main__':
    print("=" * 60)
    print("YouTube to Bilibili Upload Tool")
    print("=" * 60)
    print("Open your browser and go to: http://localhost:3000")
    print("=" * 60)
    app.run(host='0.0.0.0', port=3000, debug=True)