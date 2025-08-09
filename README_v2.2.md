# YouTube to Bilibili Tool v2.2

## New in v2.2: Chinese Subtitle Support! 🎉

### Key Features
- **Automatic Chinese Subtitles**: Downloads and burns Chinese subtitles directly into videos
- **Permanent Subtitles**: Subtitles are part of the video image - always visible on Bilibili
- **Smart Language Selection**: Tries zh-Hans, zh-Hans-en (Simplified Chinese from English)
- **FFmpeg Integration**: Uses ffmpeg to burn subtitles into video frames

### How It Works

1. **Download Video**: Downloads the YouTube video in best quality
2. **Download Chinese Subtitles**: Automatically fetches Chinese subtitles (auto-translated from English if needed)
3. **Burn Subtitles**: Uses ffmpeg to permanently burn Chinese text into the video frames
4. **Upload to Bilibili**: Video with Chinese subtitles is ready for Bilibili

### Technical Details

#### The Problem We Solved
- `--embed-subs` in yt-dlp creates subtitle tracks, but Bilibili doesn't recognize them
- Embedded subtitle tracks aren't visible by default
- Many players don't show embedded subtitle tracks

#### Our Solution
- Download subtitles separately as SRT files
- Use ffmpeg's subtitle filter to burn text directly into video frames
- Subtitles become part of the image - always visible, no player support needed

### Files Changed

1. **subtitle_helper.py** (NEW)
   - Core subtitle downloading and burning logic
   - Handles multiple subtitle language fallbacks
   - FFmpeg integration for subtitle burning

2. **clean_app_v21.py** (UPDATED)
   - Integrated subtitle_helper for all downloads
   - Added debug logging for troubleshooting
   - Automatic Chinese subtitle support

### Requirements

- **ffmpeg**: Required for burning subtitles
  - macOS: Download from https://evermeet.cx/ffmpeg/
  - Place ffmpeg binary in project root
  
- **yt-dlp**: For downloading videos and subtitles
  ```bash
  pip install yt-dlp
  ```

### Usage

1. Start the web app:
   ```bash
   python clean_app_v21.py
   ```

2. Open http://localhost:3000 in your browser

3. Download any YouTube video - Chinese subtitles will be automatically added!

### Subtitle Examples

Before (no subtitles):
- Video plays without any text
- Viewers need to understand English audio

After (with burned Chinese subtitles):
- Chinese text appears at the bottom of the video
- Text is always visible
- Perfect for Bilibili audience

### Troubleshooting

1. **No subtitles appearing?**
   - Check console output for subtitle download status
   - Ensure ffmpeg is in the correct path
   - Some videos may not have auto-generated subtitles

2. **Rate limiting errors?**
   - YouTube may rate limit subtitle downloads
   - Wait a few minutes and try again

3. **FFmpeg errors?**
   - Ensure ffmpeg binary is executable: `chmod +x ffmpeg`
   - Check ffmpeg path in subtitle_helper.py

### Version History

- **v2.2** (Current): Added Chinese subtitle support
- **v2.1**: Added video deletion and custom cover features
- **v2.0**: Clean separated workflow interface
- **v1.0**: Initial working version