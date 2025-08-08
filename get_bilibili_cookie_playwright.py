#!/usr/bin/env python3
"""
Use Playwright to visit Bilibili and get cookies
Note: This will only get non-authenticated cookies unless you login
"""

from playwright.sync_api import sync_playwright
import json
import time

def get_bilibili_cookies():
    """Visit Bilibili and extract cookies"""
    
    with sync_playwright() as p:
        # Launch browser (headless=False to see what's happening)
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        
        print("🌐 Opening Bilibili.com...")
        page.goto("https://www.bilibili.com")
        
        # Wait for page to load
        page.wait_for_load_state("networkidle")
        time.sleep(3)  # Extra wait for dynamic content
        
        print("🍪 Getting cookies...")
        cookies = context.cookies()
        
        # Extract important cookies
        cookie_dict = {}
        for cookie in cookies:
            cookie_dict[cookie['name']] = cookie['value']
        
        # Check for important Bilibili cookies
        important_cookies = ['SESSDATA', 'bili_jct', 'DedeUserID', 'DedeUserID__ckMd5']
        found_cookies = {}
        
        for name in important_cookies:
            if name in cookie_dict:
                found_cookies[name] = cookie_dict[name]
                print(f"✅ Found: {name}")
            else:
                print(f"❌ Not found: {name} (need to login)")
        
        # Format as cookie string
        if found_cookies:
            cookie_string = "; ".join([f"{k}={v}" for k, v in found_cookies.items()])
            print("\n📋 Cookie string (if any authenticated cookies found):")
            print(cookie_string)
        else:
            print("\n⚠️ No authenticated cookies found!")
            print("This is expected - you need to login manually to get valid cookies")
            
        # Show all cookies for reference
        print("\n📦 All cookies found:")
        all_cookies_string = "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        print(all_cookies_string[:200] + "..." if len(all_cookies_string) > 200 else all_cookies_string)
        
        # Save to file
        with open('bilibili_cookies.json', 'w') as f:
            json.dump(cookies, f, indent=2)
        print("\n💾 Saved all cookies to bilibili_cookies.json")
        
        # Keep browser open for manual login if needed
        print("\n" + "="*50)
        print("🔐 TO GET AUTHENTICATED COOKIES:")
        print("1. Login manually in the browser window that opened")
        print("2. After logging in, press Enter here to capture cookies")
        print("="*50)
        
        input("\nPress Enter after logging in (or Ctrl+C to cancel)...")
        
        # Get cookies again after login
        cookies_after = context.cookies()
        cookie_dict_after = {}
        for cookie in cookies_after:
            cookie_dict_after[cookie['name']] = cookie['value']
        
        # Check for authenticated cookies again
        found_after = {}
        for name in important_cookies:
            if name in cookie_dict_after:
                found_after[name] = cookie_dict_after[name]
        
        if found_after:
            auth_cookie_string = "; ".join([f"{k}={v}" for k, v in found_after.items()])
            print("\n✅ AUTHENTICATED COOKIES FOUND!")
            print("Copy this for your upload script:")
            print("\n" + "="*50)
            print(auth_cookie_string)
            print("="*50)
            
            # Save authenticated cookies
            with open('bilibili_auth_cookies.txt', 'w') as f:
                f.write(auth_cookie_string)
            print("\n💾 Saved to bilibili_auth_cookies.txt")
        
        browser.close()

if __name__ == "__main__":
    print("🚀 Bilibili Cookie Getter")
    print("-" * 40)
    get_bilibili_cookies()