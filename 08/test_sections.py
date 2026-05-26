#!/usr/bin/env python3
"""Test HTML sections split by h2 tags."""
import json, urllib.request, urllib.error, time, re

with open('/root/.hermes/wechat.json') as f:
    cred = json.load(f)
url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={cred['appId']}&secret={cred['appSecret']}"
with urllib.request.urlopen(url) as resp:
    token = json.loads(resp.read())['access_token']

with open('/root/note/yangmaji/article/08/wechat.html', 'r') as f:
    full = f.read()

# Remove the outer section wrapper
inner = full
if full.startswith('<section'):
    inner = full[full.find('>', full.find('<section'))+1:-len('</section>')]

THUMB = "kUBenucKVChUvMNC0s0WLgv8AhVjwZmvEeXG4yNAgFcjN2PLPOgO2oiHK8v8lNAY"

def test(content, label):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}"
    wrapped = f'<section>{content}</section>'
    payload = {"articles":[{"title":label,"author":"金岩","content":wrapped,"thumb_media_id":THUMB,"need_open_comment":1,"only_fans_can_comment":0}]}
    data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            r = json.loads(resp.read())
            return 'errcode' not in r
    except urllib.error.HTTPError as e:
        r = json.loads(e.read())
        print(f"  {label}: FAIL {r.get('errcode','?')}")
        return False

# Split by h2 tags
parts = re.split(r'(<h2.*?</h2>)', inner)
sections = []
current = ""
for part in parts:
    if part.startswith('<h2'):
        if current.strip():
            sections.append(current)
        current = part
    else:
        current += part
if current.strip():
    sections.append(current)

print(f"Total sections: {len(sections)}")

for i, section in enumerate(sections):
    title = f"S{i}"
    ok = test(section, title)
    print(f"  Section {i} ({len(section)} chars): {'OK' if ok else 'FAIL'}")
    if i < 3:  # Show first few chars of each
        print(f"    Start: {section[:60]}...")
    time.sleep(1)
