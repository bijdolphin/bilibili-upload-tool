#!/usr/bin/env python3
"""
YouTube to Bilibili Tool v2.1 - With Delete and Custom Cover Features
Clean web interface with separated download and upload workflow
"""

from flask import Flask, render_template_string, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import asyncio
from pathlib import Path
from bilibili_api import video_uploader, Credential
import re
import os
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

# Configuration
VIDEOS_DIR = Path("videos")
VIDEOS_DIR.mkdir(exist_ok=True)
COVERS_DIR = Path("covers")
COVERS_DIR.mkdir(exist_ok=True)

# Bilibili credentials
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOHA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6"
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"

# ... [HTML template and other routes remain the same until download function] ...

@app.route('/api/download', methods=['POST'])
def download():
    """Download YouTube video with Chinese subtitles burned in"""
    try:
        data = request.json
        youtube_url = data.get('url', '')
        
        # Extract video ID
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', youtube_url)
        if not match:
            return jsonify({'success': False, 'error': 'Invalid YouTube URL'})
        
        video_id = match.group(1)
        output_filename = f"video_{video_id}"
        output_path = VIDEOS_DIR / f"{output_filename}.mp4"
        
        print(f"[DEBUG] Starting download for: {youtube_url}")
        print(f"[DEBUG] Output filename: {output_filename}")
        
        # Import and use the subtitle helper
        try:
            from subtitle_helper import download_video_with_chinese_subtitles
            print("[DEBUG] Successfully imported subtitle_helper")
        except Exception as import_error:
            print(f"[DEBUG] Failed to import subtitle_helper: {import_error}")
            raise
        
        # Download video with Chinese subtitles burned in
        print("[DEBUG] Calling download_video_with_chinese_subtitles...")
        result_path = download_video_with_chinese_subtitles(youtube_url, output_filename)
        print(f"[DEBUG] Result path: {result_path}")
        
        if result_path and Path(result_path).exists():
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

# ... [Rest of the file remains the same] ...

if __name__ == '__main__':
    print("\n" + "="*60)
    print("YouTube to Bilibili Tool v2.2")
    print("="*60)
    print("✅ Chinese subtitle support")
    print("✅ Delete videos from library")
    print("✅ Upload custom cover images")
    print("\nOpen in browser: http://localhost:3000")
    print("="*60 + "\n")
    
    app.run(host='127.0.0.1', port=3000, debug=False)