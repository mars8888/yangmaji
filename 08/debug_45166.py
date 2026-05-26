#!/usr/bin/env python3
"""Debug 45166 error by testing HTML sections."""
import json
import urllib.request
import urllib.error
import time

# Load token
with open('/root/.hermes/wechat.json') as f:
    cred = json.load(f)

url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={cred['appId']}&secret={cred['appSecret']}"
with urllib.request.urlopen(url) as resp:
    token = json.loads(resp.read())['access_token']

# Read HTML
with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full_html = f.read()

# Try binary search to find problematic section
mid = len(full_html) // 2
half1 = full_html[:mid]
half2 = full_html[mid:]

THUMB_ID = "kUBenucKVChUvMNC0s0WLgv8AhVjwZmvEeXG4yNAgFcjN2PLPOgO2oiHK8v8lNAY"

def test_html(content, label):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {
        "articles": [{
            "title": f"测试{label}",
            "author": "金岩",
            "content": content,
            "thumb_media_id": THUMB_ID,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  {label}: OK - {result}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        result = json.loads(body)
        print(f"  {label}: FAIL - {result}")
        return False

print("Testing first half...")
test_html(half1, "前半部分")

time.sleep(1)

print("Testing second half...")
test_html(half2, "后半部分")
