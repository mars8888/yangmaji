#!/usr/bin/env python3
"""Debug 45166 - binary search on new HTML."""
import json
import urllib.request
import urllib.error
import time

with open('/root/.hermes/wechat.json') as f:
    cred = json.load(f)

url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={cred['appId']}&secret={cred['appSecret']}"
with urllib.request.urlopen(url) as resp:
    token = json.loads(resp.read())['access_token']

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full_html = f.read()

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
            if 'errcode' in result:
                print(f"  {label}: FAIL errcode={result['errcode']}")
                return False
            print(f"  {label}: OK")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        result = json.loads(body)
        print(f"  {label}: FAIL - {result}")
        return False

# Binary search
start = 0
end = len(full_html)
print(f"Total length: {end}")

for iteration in range(10):
    mid = (start + end) // 2
    if mid <= start or mid >= end:
        break
    content = full_html[start:mid]
    print(f"\nIteration {iteration+1}: testing [{start}:{mid}] ({len(content)} chars)")
    if test_html(content, f"I{iteration+1}"):
        start = mid
    else:
        end = mid
    time.sleep(1)

# Show the problematic range
print(f"\nProblematic range: [{start}:{end}]")
print(f"--- START ---")
print(full_html[start:end+200])
print(f"--- END ---")
