#!/usr/bin/env python3
"""Precise binary search for 45166 error."""
import json, urllib.request, urllib.error, time

with open('/root/.hermes/wechat.json') as f:
    cred = json.load(f)
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={cred['appId']}&secret={cred['appSecret']}"
with urllib.request.urlopen(url) as resp:
    token = json.loads(resp.read())['access_token']

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full = f.read()

THUMB = "kUBenucKVChUvMNC0s0WLgv8AhVjwZmvEeXG4yNAgFcjN2PLPOgO2oiHK8v8lNAY"

def test(content, label):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {"articles":[{"title":label,"author":"金岩","content":content,"thumb_media_id":THUMB,"need_open_comment":1,"only_fans_can_comment":0}]}
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read())
            return 'errcode' not in r
    except urllib.error.HTTPError as e:
        return False

# Verify first half is problematic
print(f"Total: {len(full)}")
print(f"First half ({len(full)//2} chars): {'OK' if test(full[:len(full)//2], 'half') else 'FAIL'}")
time.sleep(1)

# Verify second half is OK
print(f"Second half ({len(full) - len(full)//2} chars): {'OK' if test(full[len(full)//2:], 'half2') else 'FAIL'}")
time.sleep(1)

# Binary search on first half
lo, hi = 0, len(full) // 2
for _ in range(15):
    mid = (lo + hi) // 2
    if mid == lo:
        break
    ok = test(full[:mid], f"m{_}")
    if ok:
        lo = mid
    else:
        hi = mid
    time.sleep(0.5)

print(f"\nProblematic range: [{lo}:{hi}]")
print(f"Content around break point:")
print(repr(full[max(0,lo-20):hi+40]))
print()
print("Full context:")
print(full[max(0,lo-100):hi+100])
