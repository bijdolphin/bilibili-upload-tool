#!/usr/bin/env python3
"""
Open Bilibili in browser and help extract cookies after manual login
"""

from playwright.sync_api import sync_playwright
import json
import time

def open_bilibili_and_wait():
    """Open Bilibili and keep browser open for manual login"""
    
    with sync_playwright() as p:
        # Launch browser in non-headless mode so you can see it
        print("🚀 Launching Chrome browser...")
        browser = p.chromium.launch(
            headless=False,
            slow_mo=500  # Slow down actions to be visible
        )
        
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        page = context.new_page()
        
        print("🌐 Opening Bilibili.com...")
        page.goto("https://www.bilibili.com")
        
        print("\n" + "="*60)
        print("📝 INSTRUCTIONS:")
        print("="*60)
        print("1. The browser window is now open")
        print("2. Please LOGIN to your Bilibili account")
        print("3. After logging in successfully, come back here")
        print("4. The cookies will be saved automatically")
        print("="*60)
        
        # Keep checking for login status
        print("\n⏳ Waiting for login... (checking every 5 seconds)")
        
        max_wait = 300  # Wait max 5 minutes
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(5)
            elapsed += 5
            
            # Get current cookies
            cookies = context.cookies()
            cookie_dict = {}
            for cookie in cookies:
                cookie_dict[cookie['name']] = cookie['value']
            
            # Check if logged in (has SESSDATA)
            if 'SESSDATA' in cookie_dict:
                print("\n✅ Login detected! Extracting cookies...")
                
                # Extract important cookies
                important = ['SESSDATA', 'bili_jct', 'DedeUserID', 'DedeUserID__ckMd5']
                found = {}
                
                for name in important:
                    if name in cookie_dict:
                        found[name] = cookie_dict[name]
                        print(f"  ✓ {name}: {cookie_dict[name][:20]}...")
                
                # Create cookie string
                cookie_string = "; ".join([f"{k}={v}" for k, v in found.items()])
                
                # Save to file
                with open('bilibili_cookies.txt', 'w') as f:
                    f.write(cookie_string)
                
                print("\n" + "="*60)
                print("🎉 SUCCESS! Cookies saved to bilibili_cookies.txt")
                print("="*60)
                print("\n📋 Your cookie string (for the upload script):\n")
                print(cookie_string)
                print("\n" + "="*60)
                
                # Also update the quick upload script
                try:
                    with open('quick_bilibili_upload.py', 'r') as f:
                        content = f.read()
                    
                    content = content.replace('PASTE_YOUR_COOKIES_HERE', cookie_string)
                    
                    with open('quick_bilibili_upload.py', 'w') as f:
                        f.write(content)
                    
                    print("✅ Updated quick_bilibili_upload.py with your cookies!")
                    print("\n🚀 You can now run: python quick_bilibili_upload.py")
                except:
                    print("⚠️ Please manually paste the cookies into quick_bilibili_upload.py")
                
                break
            else:
                print(f"  Still waiting... ({elapsed}s elapsed)")
        
        print("\n🔄 Closing browser in 5 seconds...")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    print("🍪 Bilibili Cookie Helper")
    print("-" * 40)
    open_bilibili_and_wait()