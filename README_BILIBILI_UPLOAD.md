# Bilibili Upload Tool - Working Version

A simplified and working tool for uploading videos from YouTube to Bilibili using the modern bilibili-api-python library.

## Successfully Tested Features

- ✅ Download YouTube videos using yt-dlp
- ✅ Automatic cover image generation with PIL
- ✅ Cookie-based authentication with Playwright
- ✅ Upload to Bilibili with Chinese metadata
- ✅ Progress tracking during upload
- ✅ Support for reposted content with source attribution

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install bilibili-api-python
pip install pillow
pip install playwright
playwright install chromium

# Install yt-dlp (for YouTube downloads)
brew install yt-dlp  # macOS
# Or: pip install yt-dlp
```

### 2. Get Bilibili Cookies

```bash
# Open Bilibili in browser for login
python open_bilibili_for_login.py

# After logging in, extract cookies
python get_bilibili_cookie_playwright.py
```

Update the extracted cookies in `bilibili_upload_final_working.py`.

### 3. Download and Upload

```bash
# Download YouTube video
yt-dlp -o "videos/%(title)s.%(ext)s" https://www.youtube.com/watch?v=VIDEO_ID

# Upload to Bilibili
python bilibili_upload_final_working.py videos/your_video.mp4
```

## Working Files

- **`bilibili_upload_final_working.py`** - Main upload script (WORKING VERSION)
- **`minimal_upload.py`** - Minimal working example for testing
- **`create_cover.py`** - Generates cover images for videos
- **`get_bilibili_cookie_playwright.py`** - Cookie extraction tool
- **`open_bilibili_for_login.py`** - Browser automation for login
- **`test_bilibili_simple.py`** - Test authentication

## Successfully Uploaded Example

- First YouTube video "Me at the zoo" uploaded to Bilibili
- URL: https://www.bilibili.com/video/BV1abt1zMER9
- Title: 我在动物园 - 第一个YouTube视频 🎬

## Required Cookies

Update these in `bilibili_upload_final_working.py`:
- `SESSDATA` - Session cookie
- `BILI_JCT` - CSRF token  
- `BUVID3` - Device identifier

## Important Notes

- Videos must be MP4 format (H.264 codec recommended)
- Maximum file size: 8GB
- Cookies expire periodically - re-login if upload fails
- Videos may take a few minutes to process on Bilibili

## Troubleshooting

If upload fails:
1. Run `test_bilibili_simple.py` to check authentication
2. Refresh cookies if expired
3. Ensure video format is MP4
4. Check file size < 8GB

## License

For educational purposes. Please respect copyright policies.