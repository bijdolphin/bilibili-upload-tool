#!/bin/bash
#
# Smart Upload Script for China Users
# Automatically handles VPN/proxy switching
#

echo "=================================================="
echo "Smart Bilibili Upload for China"
echo "=================================================="

VIDEO_PATH="${1:-videos/video_jNQXAC9IVRw.mp4}"

if [ ! -f "$VIDEO_PATH" ]; then
    echo "❌ Video not found: $VIDEO_PATH"
    exit 1
fi

echo "📹 Video: $VIDEO_PATH"
echo ""

# Step 1: Check if we need to download from YouTube
if [ ! -z "$2" ]; then
    YOUTUBE_URL="$2"
    echo "Step 1: Downloading from YouTube (needs VPN)"
    echo "URL: $YOUTUBE_URL"
    echo ""
    
    # Enable proxy for YouTube download
    export HTTP_PROXY=http://127.0.0.1:7890
    export HTTPS_PROXY=http://127.0.0.1:7890
    
    echo "🌐 Proxy enabled for YouTube"
    yt-dlp -f "best[ext=mp4]/best" -o "$VIDEO_PATH" "$YOUTUBE_URL"
    
    if [ $? -ne 0 ]; then
        echo "❌ Download failed. Make sure ClashX is running."
        exit 1
    fi
    echo "✅ Download complete"
    echo ""
fi

# Step 2: Upload to Bilibili (try without proxy first)
echo "Step 2: Uploading to Bilibili"
echo ""

# First attempt: Direct connection (no proxy)
echo "Attempting direct connection (recommended for China)..."
unset HTTP_PROXY
unset HTTPS_PROXY
unset http_proxy
unset https_proxy

source venv/bin/activate
python bilibili_upload_ssl_fix.py "$VIDEO_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Upload successful!"
    exit 0
fi

echo ""
echo "Direct connection failed. Trying with proxy..."
echo ""

# Second attempt: With proxy
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

python bilibili_upload_proxy.py "$VIDEO_PATH"

if [ $? -eq 0 ]; then
    echo "✅ Upload successful with proxy!"
    exit 0
fi

echo ""
echo "=================================================="
echo "Both methods failed. Possible solutions:"
echo "1. Update cookies (login to Bilibili again)"
echo "2. Try at a different time (network issues)"
echo "3. Manually upload the downloaded video"
echo "   File: $VIDEO_PATH"
echo "=================================================="