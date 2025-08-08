#!/usr/bin/env python3
"""
Create a simple cover image for video upload
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_cover():
    # Create a new image with a nice gradient background
    width, height = 1920, 1080
    img = Image.new('RGB', (width, height), color='#2E3440')
    
    # Create a gradient effect
    draw = ImageDraw.Draw(img)
    
    # Draw gradient background
    for i in range(height):
        color_value = int(46 + (i / height) * 20)  # Gradient from dark to slightly lighter
        color = (color_value, color_value + 4, color_value + 16)  # Slight blue tint
        draw.rectangle([(0, i), (width, i + 1)], fill=color)
    
    # Add text
    try:
        # Try to use a system font
        font_large = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
        font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw title
    title = "Me at the Zoo"
    subtitle = "第一个YouTube视频"
    date = "2005.04.23"
    
    # Calculate text positions for centering
    bbox = draw.textbbox((0, 0), title, font=font_large)
    title_width = bbox[2] - bbox[0]
    title_height = bbox[3] - bbox[1]
    
    # Draw main title
    draw.text(
        ((width - title_width) // 2, height // 2 - 150),
        title,
        fill='#ECEFF4',
        font=font_large
    )
    
    # Draw subtitle
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    subtitle_width = bbox[2] - bbox[0]
    draw.text(
        ((width - subtitle_width) // 2, height // 2),
        subtitle,
        fill='#D8DEE9',
        font=font_small
    )
    
    # Draw date
    bbox = draw.textbbox((0, 0), date, font=font_small)
    date_width = bbox[2] - bbox[0]
    draw.text(
        ((width - date_width) // 2, height // 2 + 100),
        date,
        fill='#81A1C1',
        font=font_small
    )
    
    # Add some decorative elements
    # Top and bottom bars
    draw.rectangle([(0, 0), (width, 5)], fill='#5E81AC')
    draw.rectangle([(0, height - 5), (width, height)], fill='#5E81AC')
    
    # Save the image
    img.save('cover.jpg', 'JPEG', quality=95)
    print("✅ Cover image created: cover.jpg")
    return 'cover.jpg'

if __name__ == "__main__":
    cover_path = create_cover()
    print(f"📸 Cover saved at: {cover_path}")
    print(f"📐 Size: 1920x1080")