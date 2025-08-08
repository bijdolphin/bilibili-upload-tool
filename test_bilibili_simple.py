#!/usr/bin/env python3
"""
Simple test of bilibili-api-python
"""

import asyncio
from bilibili_api import Credential, user

# Your cookies
SESSDATA = "1800c717%2C1770189047%2C51090%2A81CjB78IVHv80KKSBHcKChq-Fqhl3SRO_Yl-9QHL5Vbc030rai9ciWKeGHGzJde488iXoSVjh6UXFiWU9BOWdENHVjRTI0RklxVzFibmU4bW1WOFA0RHIyTnRwdUVWRG55VWdHbkFMZ1RscXVwdXdwZHdrY0ZwcDdMQnVnWXUyT2RlMXlTVVA0aFhRIIEC"
BILI_JCT = "ab82678dab4d309107592e13eaadc3a6" 
BUVID3 = "A588F085-9787-B1E8-16D9-F533825C40BB43049infoc"
DEDEUSERID = "456502519"

async def test_login():
    """Test if we can login with cookies"""
    
    print("Testing Bilibili API authentication...")
    
    try:
        # Create credential
        credential = Credential(
            sessdata=SESSDATA,
            bili_jct=BILI_JCT,
            buvid3=BUVID3,
            dedeuserid=DEDEUSERID
        )
        
        # Test by getting user info
        u = user.User(uid=int(DEDEUSERID), credential=credential)
        info = await u.get_user_info()
        
        print(f"✅ Login successful!")
        print(f"👤 Username: {info.get('name', 'Unknown')}")
        print(f"🆔 UID: {info.get('mid', 'Unknown')}")
        print(f"📊 Level: {info.get('level', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_login())
    
    if success:
        print("\n✅ Your cookies are valid! You can proceed with upload.")
    else:
        print("\n❌ Cookie authentication failed.")
        print("Please get fresh cookies from bilibili.com")