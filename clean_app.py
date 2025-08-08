#!/usr/bin/env python3
"""
YouTube to Bilibili Tool - Clean Version
Separated download and upload workflow
"""

from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import subprocess
import asyncio
from pathlib import Path
from bilibili_api import video_uploader, Credential
import re

app = Flask(__name__)
CORS(app)

# Configuration
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)

# Bilibili credentials
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOHA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6"
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <title>YouTube to Bilibili</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            margin-bottom: 10px;
            font-size: 36px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            color: rgba(255,255,255,0.95);
            text-align: center;
            margin-bottom: 40px;
            font-size: 18px;
        }
        
        .workflow {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 30px;
            margin-bottom: 30px;
            align-items: start;
        }
        
        @media (max-width: 968px) {
            .workflow {
                grid-template-columns: 1fr;
                gap: 20px;
            }
            .arrow {
                display: none;
            }
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h2 {
            margin-bottom: 15px;
            color: #333;
            font-size: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .card-icon {
            font-size: 32px;
        }
        
        .card-description {
            color: #666;
            margin-bottom: 25px;
            font-size: 15px;
            line-height: 1.5;
        }
        
        .arrow {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            color: white;
            opacity: 0.8;
            padding-top: 100px;
        }
        
        input[type="url"], input[type="text"], select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            font-size: 15px;
            margin-bottom: 18px;
            transition: all 0.3s;
            background: #fafafa;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
            background: white;
        }
        
        button {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 12px;
            font-size: 17px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .download-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .download-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(102, 126, 234, 0.4);
        }
        
        .upload-btn {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        
        .upload-btn:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(245, 87, 108, 0.4);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 20px;
            padding: 16px;
            border-radius: 12px;
            display: none;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .status.show {
            display: block;
        }
        
        .success {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border: 1px solid #b1dfbb;
        }
        
        .error {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c2c7 100%);
            color: #721c24;
            border: 1px solid #f1aeb5;
        }
        
        .processing {
            background: linear-gradient(135deg, #cce5ff 0%, #b8daff 100%);
            color: #004085;
            border: 1px solid #9ec5fe;
        }
        
        .video-library {
            background: white;
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .video-library h3 {
            margin-bottom: 25px;
            color: #333;
            font-size: 22px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }
        
        .video-item {
            display: flex;
            flex-direction: column;
            padding: 18px;
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 12px;
            transition: all 0.3s;
            border: 2px solid transparent;
        }
        
        .video-item:hover {
            border-color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .video-name {
            color: #333;
            font-size: 14px;
            font-weight: 500;
            margin-bottom: 8px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }
        
        .video-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: auto;
        }
        
        .video-size {
            color: #999;
            font-size: 13px;
        }
        
        .select-btn {
            padding: 8px 16px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .select-btn:hover {
            background: #5a67d8;
            transform: translateY(-1px);
        }
        
        .no-videos {
            grid-column: 1 / -1;
            color: #999;
            text-align: center;
            padding: 60px 20px;
            font-size: 16px;
        }
        
        .no-videos::before {
            content: "📭";
            display: block;
            font-size: 48px;
            margin-bottom: 15px;
            opacity: 0.5;
        }
        
        .spinner {
            display: inline-block;
            width: 18px;
            height: 18px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .stats {
            display: flex;
            gap: 30px;
            margin-bottom: 30px;
            justify-content: center;
        }
        
        .stat-card {
            background: white;
            padding: 20px 40px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 YouTube to Bilibili</h1>
        <p class="subtitle">Download from YouTube • Upload to Bilibili</p>
        
        <div class="stats" id="stats">
            <div class="stat-card">
                <div class="stat-number" id="downloadCount">0</div>
                <div class="stat-label">Videos Downloaded</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="uploadCount">0</div>
                <div class="stat-label">Videos Uploaded</div>
            </div>
        </div>
        
        <div class="workflow">
            <!-- Step 1: Download -->
            <div class="card">
                <h2>
                    <span class="card-icon">⬇️</span>
                    Step 1: Download
                </h2>
                
                <p class="card-description">
                    Download videos from YouTube to your local storage
                </p>
                
                <form id="downloadForm">
                    <input 
                        type="url" 
                        id="youtubeUrl" 
                        placeholder="Enter YouTube URL" 
                        required
                    >
                    <button type="submit" class="download-btn" id="downloadBtn">
                        Download Video
                    </button>
                </form>
                
                <div id="downloadStatus" class="status"></div>
            </div>
            
            <!-- Arrow -->
            <div class="arrow">→</div>
            
            <!-- Step 2: Upload -->
            <div class="card">
                <h2>
                    <span class="card-icon">⬆️</span>
                    Step 2: Upload
                </h2>
                
                <p class="card-description">
                    Select a downloaded video and upload it to Bilibili
                </p>
                
                <form id="uploadForm">
                    <select id="videoSelect" required>
                        <option value="">Select a video...</option>
                    </select>
                    <input 
                        type="text" 
                        id="videoTitle" 
                        placeholder="Custom title (optional)" 
                    >
                    <button type="submit" class="upload-btn" id="uploadBtn">
                        Upload to Bilibili
                    </button>
                </form>
                
                <div id="uploadStatus" class="status"></div>
            </div>
        </div>
        
        <!-- Video Library -->
        <div class="video-library">
            <h3>📚 Video Library</h3>
            <div class="video-grid" id="videoList">
                <div class="no-videos">No videos yet. Download some videos to get started!</div>
            </div>
        </div>
    </div>
    
    <script>
        let downloadCount = 0;
        let uploadCount = 0;
        
        // Load video list on page load
        loadVideoList();
        
        // Refresh video list every 3 seconds
        setInterval(loadVideoList, 3000);
        
        async function loadVideoList() {
            try {
                const response = await fetch('/api/videos');
                const videos = await response.json();
                
                const videoList = document.getElementById('videoList');
                const videoSelect = document.getElementById('videoSelect');
                
                // Update download count
                document.getElementById('downloadCount').textContent = videos.length;
                
                if (videos.length === 0) {
                    videoList.innerHTML = '<div class="no-videos">No videos yet. Download some videos to get started!</div>';
                    videoSelect.innerHTML = '<option value="">Select a video...</option>';
                } else {
                    // Update grid display
                    videoList.innerHTML = videos.map(video => `
                        <div class="video-item">
                            <div class="video-name" title="${video.name}">📹 ${video.name}</div>
                            <div class="video-meta">
                                <span class="video-size">${video.size}</span>
                                <button class="select-btn" onclick="selectVideo('${video.path}')">Select</button>
                            </div>
                        </div>
                    `).join('');
                    
                    // Update select options
                    const currentValue = videoSelect.value;
                    videoSelect.innerHTML = '<option value="">Select a video...</option>' +
                        videos.map(video => `
                            <option value="${video.path}">${video.name}</option>
                        `).join('');
                    
                    // Restore selection
                    if (currentValue && videos.some(v => v.path === currentValue)) {
                        videoSelect.value = currentValue;
                    }
                }
            } catch (error) {
                console.error('Failed to load videos:', error);
            }
        }
        
        function selectVideo(path) {
            document.getElementById('videoSelect').value = path;
            document.getElementById('uploadForm').scrollIntoView({ behavior: 'smooth' });
        }
        
        // Download form handler
        document.getElementById('downloadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const url = document.getElementById('youtubeUrl').value;
            const btn = document.getElementById('downloadBtn');
            const status = document.getElementById('downloadStatus');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Downloading...';
            status.className = 'status processing show';
            status.innerHTML = '⏳ Downloading video, please wait...';
            
            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    status.className = 'status success show';
                    status.innerHTML = `✅ Download complete!<br>File: ${result.filename}<br>Size: ${result.size}`;
                    loadVideoList();
                    document.getElementById('youtubeUrl').value = '';
                    downloadCount++;
                } else {
                    status.className = 'status error show';
                    status.innerHTML = `❌ Download failed: ${result.error}`;
                }
            } catch (error) {
                status.className = 'status error show';
                status.innerHTML = `❌ Error: ${error.message}`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Download Video';
            }
        });
        
        // Upload form handler
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const videoPath = document.getElementById('videoSelect').value;
            const title = document.getElementById('videoTitle').value;
            
            if (!videoPath) {
                alert('Please select a video to upload');
                return;
            }
            
            const btn = document.getElementById('uploadBtn');
            const status = document.getElementById('uploadStatus');
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Uploading...';
            status.className = 'status processing show';
            status.innerHTML = '⏳ Uploading to Bilibili, please wait...';
            
            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({video_path: videoPath, title})
                });
                
                const result = await response.json();
                
                if (result.success) {
                    status.className = 'status success show';
                    status.innerHTML = `✅ Upload successful!<br>
                        <a href="${result.url}" target="_blank" style="color: #007bff;">View on Bilibili (${result.bvid})</a>`;
                    document.getElementById('videoTitle').value = '';
                    uploadCount++;
                    document.getElementById('uploadCount').textContent = uploadCount;
                } else {
                    status.className = 'status error show';
                    status.innerHTML = `❌ Upload failed: ${result.error}`;
                }
            } catch (error) {
                status.className = 'status error show';
                status.innerHTML = `❌ Error: ${error.message}`;
            } finally {
                btn.disabled = false;
                btn.innerHTML = 'Upload to Bilibili';
            }
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/videos')
def list_videos():
    """List all downloaded videos"""
    videos = []
    for video in VIDEOS_DIR.glob("*.mp4"):
        size = video.stat().st_size
        size_mb = size / (1024 * 1024)
        videos.append({
            "name": video.name,
            "path": str(video),
            "size": f"{size_mb:.1f} MB"
        })
    return jsonify(videos)

@app.route('/api/download', methods=['POST'])
def download():
    """Download YouTube video"""
    try:
        data = request.json
        youtube_url = data.get('url', '')
        
        # Extract video ID
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
        if not match:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'})
        
        video_id = match.group(1)
        output_path = VIDEOS_DIR / f"video_{video_id}.mp4"
        
        # Download with yt-dlp
        cmd = [
            "yt-dlp",
            "-f", "best[ext=mp4]/best",
            "-o", str(output_path),
            "--no-playlist",
            youtube_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and output_path.exists():
            size = output_path.stat().st_size / (1024 * 1024)
            return jsonify({
                'success': True,
                'filename': output_path.name,
                'size': f"{size:.1f} MB"
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Download failed. Please check your connection.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/upload', methods=['POST'])
def upload():
    """Upload to Bilibili"""
    try:
        data = request.json
        video_path = data.get('video_path', '')
        custom_title = data.get('title', '')
        
        if not Path(video_path).exists():
            return jsonify({'success': False, 'error': 'Video file not found'})
        
        # Upload to Bilibili
        async def do_upload():
            # Create cover if needed
            cover_file = Path("cover.jpg")
            if not cover_file.exists():
                subprocess.run(["python", "create_cover.py"], check=True)
            
            # Create credential
            credential = Credential(
                sessdata=SESSDATA,
                bili_jct=BILI_JCT,
                buvid3=BUVID3
            )
            
            # Prepare metadata
            video_file = Path(video_path)
            title = custom_title or f"YouTube Video - {video_file.stem}"
            title = title[:80]  # Bilibili title limit
            
            meta = {
                "copyright": 2,  # Repost
                "source": "YouTube",
                "tid": 21,  # Daily category
                "title": title,
                "desc_format_id": 0,
                "desc": "Video from YouTube",
                "dynamic": "",
                "tags": ["YouTube", "Video"],
            }
            
            # Create uploader
            upload_args = {
                "pages": [
                    video_uploader.VideoUploaderPage(
                        path=str(video_file.resolve()),
                        title=title,
                        description=""
                    )
                ],
                "meta": meta,
                "credential": credential
            }
            
            if cover_file.exists():
                upload_args["cover"] = str(cover_file.resolve())
            
            uploader = video_uploader.VideoUploader(**upload_args)
            result = await uploader.start()
            
            return result
        
        # Run async upload
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        upload_result = loop.run_until_complete(do_upload())
        loop.close()
        
        if upload_result:
            bvid = upload_result.get('bvid')
            return jsonify({
                'success': True,
                'bvid': bvid,
                'url': f'https://www.bilibili.com/video/{bvid}'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Upload failed. Please try again.'
            })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("YouTube to Bilibili Tool")
    print("="*60)
    print("Clean interface with separated workflow")
    print("\nOpen in browser: http://localhost:3000")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=3000, debug=False)