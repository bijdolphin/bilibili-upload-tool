#!/usr/bin/env python3
"""
Minimal Bilibili upload test
"""

import asyncio
from pathlib import Path
from bilibili_api import video_uploader, Credential
import os

# Credentials
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOFA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6"
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"

async def upload():
    print("Starting minimal upload test...")
    
    # Get absolute paths
    video_path = Path("videos/test_video.mp4").resolve()
    cover_path = Path("cover.jpg").resolve()
    
    print(f"Video: {video_path}")
    print(f"Cover: {cover_path}")
    print(f"Video exists: {video_path.exists()}")
    print(f"Cover exists: {cover_path.exists()}")
    
    # Create credential
    credential = Credential(
        sessdata=SESSDATA,
        bili_jct=BILI_JCT,
        buvid3=BUVID3
    )
    
    # Minimal meta (without cover for now)
    meta = {
        "copyright": 2,
        "source": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
        "tid": 21,
        "title": "测试视频上传",
        "desc_format_id": 0,
        "desc": "这是一个测试视频",
        "dynamic": "",
        "tags": ["测试"],
    }
    
    # Create uploader
    uploader = video_uploader.VideoUploader(
        pages=[
            video_uploader.VideoUploaderPage(
                path=str(video_path),
                title="测试",
                description=""
            )
        ],
        meta=meta,
        credential=credential,
        cover=str(cover_path)  # Pass cover separately
    )
    
    # Add event handler
    @uploader.on("__ALL__")
    async def handler(event):
        print(f"Event: {event}")
    
    try:
        result = await uploader.start()
        print(f"Success! Result: {result}")
        if result:
            bvid = result.get('bvid', '')
            print(f"Video URL: https://www.bilibili.com/video/{bvid}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(upload())