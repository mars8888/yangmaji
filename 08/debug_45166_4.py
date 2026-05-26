#!/usr/bin/env python3
"""Debug 45166 - split E1 further."""
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

# E1 was 0 to q1_end//2 = 0 to len//8
e1_end = len(full_html) // 8
e1 = full_html[:e1_end]

# Split E1
f1 = e1[:len(e1)//2]
f2 = e1[len(e1)//2:]

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

print(f"E1 length: {len(e1)}")
print("Testing F1 (0-6.25%)...")
test_html(f1, "F1")
time.sleep(1)

print("Testing F2 (6.25-12.5%)...")
test_html(f2, "F2")
