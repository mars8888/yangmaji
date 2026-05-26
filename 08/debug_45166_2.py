#!/usr/bin/env python3
"""Debug 45166 error - narrow down to specific section."""
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

# First half was problematic
mid = len(full_html) // 2
first_half = full_html[:mid]

# Split first half into quarters
q1 = first_half[:len(first_half)//2]
q2 = first_half[len(first_half)//2:]

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
                print(f"  {label}: FAIL - {result}")
                return False
            print(f"  {label}: OK - media_id={result.get('media_id', '?')}")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        result = json.loads(body)
        print(f"  {label}: FAIL - {result}")
        return False

print("Testing quarter 1 (0-25%)...")
test_html(q1, "Q1")
time.sleep(1)

print("Testing quarter 2 (25-50%)...")
test_html(q2, "Q2")
