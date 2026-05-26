#!/usr/bin/env python3
"""Show exact problematic content with context."""
with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full_html = f.read()

# Show range 1100-1250
print(f"Range [1100:1250]:")
print(full_html[1100:1250])
print()
print("REPR:")
print(repr(full_html[1100:1250]))
print()

# Test: does 0:1118 pass?
import json, urllib.request, urllib.error

with open('/root/.hermes/wechat.json') as f:
    cred = json.load(f)
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={cred['appId']}&secret={cred['appSecret']}"
with urllib.request.urlopen(url) as resp:
    token = json.loads(resp.read())['access_token']

THUMB = "kUBenucKVChUvMNC0s0WLgv8AhVjwZmvEeXG4yNAgFcjN2PLPOgO2oiHK8v8lNAY"

def test(content, label):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    payload = {"articles":[{"title":label,"author":"金岩","content":content,"thumb_media_id":THUMB,"need_open_comment":1,"only_fans_can_comment":0}]}
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read())
            ok = 'errcode' not in r
            print(f"  {label} ({len(content)} chars): {'OK' if ok else 'FAIL ' + str(r.get('errcode','?'))}")
            return ok
    except urllib.error.HTTPError as e:
        r = json.loads(e.read())
        print(f"  {label} ({len(content)} chars): FAIL {r.get('errcode','?')}")
        return False

# Test exact boundaries
print("\nTesting boundaries:")
test(full_html[:1118], "1118")
import time; time.sleep(0.5)
test(full_html[:1119], "1119")
time.sleep(0.5)
test(full_html[:1120], "1120")
time.sleep(0.5)
test(full_html[:1130], "1130")
time.sleep(0.5)
test(full_html[:1140], "1140")
