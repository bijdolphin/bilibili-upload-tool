# YouTube to Bilibili Tool v2.0

A complete web-based tool for downloading YouTube videos and uploading them to Bilibili with a clean, separated workflow.

## v2.0 Features

- 🌐 **Clean Web Interface** - Modern, user-friendly design
- ⬇️ **Step 1: Download** - Download YouTube videos locally
- ⬆️ **Step 2: Upload** - Upload videos to Bilibili
- 📚 **Video Library** - Manage your downloaded videos
- 📊 **Statistics** - Track downloads and uploads
- 🎨 **Auto Cover Generation** - Automatic cover image creation
- 📱 **Responsive Design** - Works on all devices

## Successfully Tested

- ✅ Complete workflow tested and working
- ✅ Downloaded and uploaded "Me at the zoo" (first YouTube video)
- ✅ Works with various network configurations
- ✅ Clean, separated workflow for better organization

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

### 3. Run the Web Application

```bash
# Start the web server
python clean_app.py
```

Then open http://localhost:3000 in your browser.

### 4. Use the Interface

1. **Step 1**: Enter a YouTube URL and click "Download Video"
2. **Step 2**: Select a downloaded video and click "Upload to Bilibili"
3. **Monitor**: View your video library and upload statistics

## Key Files (v2.0)

- **`clean_app.py`** - Main web application (v2.0)
- **`bilibili_upload_final_working.py`** - Command-line upload script
- **`create_cover.py`** - Generates cover images for videos
- **`get_bilibili_cookie_playwright.py`** - Cookie extraction tool
- **`templates/index.html`** - Web interface template

## Legacy Files (v1.0)

- **`minimal_upload.py`** - Minimal working example for testing
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