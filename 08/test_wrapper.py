#!/usr/bin/env python3
"""Test content length threshold."""
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
            return 'errcode' not in r, r
    except urllib.error.HTTPError as e:
        r = json.loads(e.read())
        return False, r

# Test full content without the section wrapper
# First, let me check: is the <section> wrapper causing issues?
inner = full[len('<section style="margin:0;padding:0;font-family:-apple-system,Helvetica Neue,Helvetica,Arial,sans-serif;">'):-len('</section>')]
print(f"Inner length: {len(inner)}")
ok, r = test(inner, "无section")
print(f"Without section wrapper: {'OK' if ok else 'FAIL ' + str(r.get('errcode','?'))}")
time.sleep(1)

# Test with just section wrapper
ok2, r2 = test(full, "有section")
print(f"With section wrapper: {'OK' if ok2 else 'FAIL ' + str(r2.get('errcode','?'))}")
time.sleep(1)

# Test with minimal wrapper
minimal = f'<div>{inner}</div>'
ok3, r3 = test(minimal, "div包装")
print(f"With div wrapper: {'OK' if ok3 else 'FAIL ' + str(r3.get('errcode','?'))}")
time.sleep(1)

# Test with no wrapper at all
ok4, r4 = test(inner, "无包装")
print(f"Without any wrapper: {'OK' if ok4 else 'FAIL ' + str(r4.get('errcode','?'))}")
