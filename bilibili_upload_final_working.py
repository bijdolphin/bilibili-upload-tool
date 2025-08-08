#!/usr/bin/env python3
"""
Bilibili Upload - Final Working Version
Successfully uploads videos to Bilibili using bilibili-api-python
"""

import asyncio
from pathlib import Path
from bilibili_api import video_uploader, Credential
import sys

# Your Bilibili credentials
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOFA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6"
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"

async def upload_video(
    video_path: str,
    title: str = "我在动物园 - 第一个YouTube视频 🎬",
    desc: str = None,
    tags: list = None,
    cover_path: str = None
):
    """
    Upload a video to Bilibili
    
    Args:
        video_path: Path to the video file
        title: Video title
        desc: Video description
        tags: List of tags
        cover_path: Path to cover image (optional)
    """
    
    if desc is None:
        desc = """YouTube上的第一个视频，上传于2005年4月23日。
视频中创始人在圣地亚哥动物园谈论大象。
这是互联网视频历史上具有里程碑意义的一刻。

原视频：https://www.youtube.com/watch?v=jNQXAC9IVRw"""
    
    if tags is None:
        tags = ["YouTube历史", "第一个视频", "动物园", "大象", "经典", "互联网"]
    
    print("🚀 Bilibili Video Upload Tool")
    print("=" * 50)
    
    # Check video exists
    video_file = Path(video_path).resolve()
    if not video_file.exists():
        print(f"❌ Video not found: {video_path}")
        return False
    
    print(f"📹 Video: {video_file.name}")
    print(f"📝 Title: {title}")
    print(f"🏷️ Tags: {', '.join(tags)}")
    
    # Check/create cover
    if cover_path:
        cover_file = Path(cover_path).resolve()
        if not cover_file.exists():
            print(f"⚠️ Cover not found: {cover_path}")
            cover_file = None
    else:
        # Try to use default cover if it exists
        cover_file = Path("cover.jpg").resolve()
        if not cover_file.exists():
            print("Creating cover image...")
            try:
                import subprocess
                subprocess.run(["python", "create_cover.py"], check=True)
                if cover_file.exists():
                    print("✅ Cover created")
            except:
                print("⚠️ Could not create cover, uploading without")
                cover_file = None
    
    if cover_file and cover_file.exists():
        print(f"🖼️ Cover: {cover_file.name}")
    
    print("-" * 50)
    
    try:
        # Create credential
        credential = Credential(
            sessdata=SESSDATA,
            bili_jct=BILI_JCT,
            buvid3=BUVID3
        )
        
        print("✅ Authentication successful")
        
        # Meta data
        meta = {
            "copyright": 2,  # 1=原创, 2=转载
            "source": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "tid": 21,  # 21=日常分区
            "title": title,
            "desc_format_id": 0,
            "desc": desc,
            "dynamic": "",
            "tags": tags,
        }
        
        # Create uploader
        print("\n⬆️ Uploading to Bilibili...")
        print("This may take a few minutes depending on file size...")
        
        # Prepare upload arguments
        upload_args = {
            "pages": [
                video_uploader.VideoUploaderPage(
                    path=str(video_file),
                    title=title[:80],  # Title limit
                    description=""
                )
            ],
            "meta": meta,
            "credential": credential
        }
        
        # Add cover if available
        if cover_file and cover_file.exists():
            upload_args["cover"] = str(cover_file)
        
        uploader = video_uploader.VideoUploader(**upload_args)
        
        # Progress tracking
        upload_progress = {"chunks": 0, "total_chunks": 0}
        
        @uploader.on("PRE_CHUNK")
        async def on_pre_chunk(data):
            upload_progress["total_chunks"] = data["total_chunk_count"]
            upload_progress["chunks"] = data["chunk_number"]
            percent = (data["chunk_number"] / data["total_chunk_count"]) * 100
            print(f"📊 Uploading: {percent:.1f}% ({data['chunk_number']}/{data['total_chunk_count']})", end="\r")
        
        @uploader.on("AFTER_CHUNK")
        async def on_after_chunk(data):
            upload_progress["chunks"] = data["chunk_number"] + 1
            percent = ((data["chunk_number"] + 1) / data["total_chunk_count"]) * 100
            print(f"📊 Uploading: {percent:.1f}% ({data['chunk_number'] + 1}/{data['total_chunk_count']})", end="\r")
        
        @uploader.on("AFTER_COVER")
        async def on_cover_uploaded(data):
            print("\n✅ Cover uploaded successfully")
        
        @uploader.on("PRE_SUBMIT")
        async def on_pre_submit(data):
            print("\n📤 Submitting video information...")
        
        # Execute upload
        result = await uploader.start()
        
        if result:
            aid = result.get('aid')
            bvid = result.get('bvid')
            
            print("\n" + "=" * 50)
            print("✅ SUCCESS! Video uploaded to Bilibili!")
            print("=" * 50)
            print(f"🎯 AID: {aid}")
            print(f"🔗 BV号: {bvid}")
            print(f"📺 Watch at: https://www.bilibili.com/video/{bvid}")
            print("=" * 50)
            
            return {
                "success": True,
                "aid": aid,
                "bvid": bvid,
                "url": f"https://www.bilibili.com/video/{bvid}"
            }
        else:
            print("\n❌ Upload failed - no result returned")
            return {"success": False}
            
    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        
        # Specific error handling
        if "登录" in str(e) or "login" in str(e).lower():
            print("\n⚠️ Authentication issue!")
            print("Your cookies may have expired.")
            print("Please:")
            print("1. Login to bilibili.com")
            print("2. Run: python open_bilibili_for_login.py")
            print("3. Update the cookies in this script")
        elif "网络" in str(e) or "network" in str(e).lower():
            print("\n⚠️ Network issue!")
            print("Please check your internet connection")
        
        return {"success": False, "error": str(e)}

def main():
    """Main entry point"""
    
    # Default video path
    video_path = "videos/test_video.mp4"
    
    # Check if video path provided as argument
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    
    # Run the upload
    result = asyncio.run(upload_video(video_path))
    
    if result["success"]:
        print("\n🎉 Congratulations on your successful upload!")
        print("📌 Note: Video may take a few minutes to be fully processed")
        print("👀 You can now view your video on Bilibili")
    else:
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure you're logged into Bilibili")
        print("2. Check that cookies are valid and not expired")
        print("3. Verify video format is MP4 with H.264 codec")
        print("4. Ensure video size is under 8GB")
        print("5. Check your network connection")

if __name__ == "__main__":
    main()