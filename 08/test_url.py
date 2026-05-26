#!/usr/bin/env python3
"""Test if the URL is the problem."""
import json, urllib.request, urllib.error, time

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
            return 'errcode' not in r
    except urllib.error.HTTPError as e:
        r = json.loads(e.read())
        return False

# Test the link 04 by itself
link04 = '<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/wechat-04" style="color:#3b82f6;text-decoration:none;">04 | 连接微信公众号发布</a></p>'
print(f"Link 04 alone: {'OK' if test(link04, 'l04') else 'FAIL'}")
time.sleep(0.5)

# Test with different URL
link04_alt = '<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://example.com/test-04" style="color:#3b82f6;text-decoration:none;">04 | 连接微信公众号发布</a></p>'
print(f"Link 04 alt URL: {'OK' if test(link04_alt, 'l04alt') else 'FAIL'}")
time.sleep(0.5)

# Test with just text (no link)
text04 = '<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;">04 | 连接微信公众号发布</p>'
print(f"Text 04 (no link): {'OK' if test(text04, 't04') else 'FAIL'}")
time.sleep(0.5)

# Test base + link 04
base = '<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px;line-height:1.4;border-bottom:2px solid #3b82f6;padding-bottom:8px;">Test</h1>'
combined = base + '\n' + link04
print(f"Base + link04: {'OK' if test(combined, 'base+l04') else 'FAIL'}")
time.sleep(0.5)

# Test: is it the wechat-04 URL specifically?
url_test = '<a href="https://mp.weixin.qq.com/s/wechat-04">test</a>'
print(f"wechat-04 URL: {'OK' if test(url_test, 'url_test') else 'FAIL'}")
