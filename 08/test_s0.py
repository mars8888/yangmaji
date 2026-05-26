#!/usr/bin/env python3
"""Test Section 0 pieces."""
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

s0 = '''<h1 style="font-size:22px;font-weight:bold;color:#1a1a1a;margin:25px 0 15px;line-height:1.4;border-bottom:2px solid #3b82f6;padding-bottom:8px;">[养马记08] 我把内容运营交给了定时任务：Cron 自动化实战</h1>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><strong style="font-weight:bold;">系列回顾：</strong></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/IkLRdrsG1OmYHHG96QkAwg" style="color:#3b82f6;text-decoration:none;">01 | 为什么放弃 OpenClaw，选择了 Hermes</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/3a0_smFwwebr6107AjpCOQ" style="color:#3b82f6;text-decoration:none;">02 | Hermes 如何接通 GitHub</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/FZom04_yctajB7EBJxvJ2w" style="color:#3b82f6;text-decoration:none;">03 | WSL 下的 OpenCLI 应用</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/wechat-04" style="color:#3b82f6;text-decoration:none;">04 | 连接微信公众号发布</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/qwen-tts-05" style="color:#3b82f6;text-decoration:none;">05 | qwen-tts 语音输出</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/mcp-06" style="color:#3b82f6;text-decoration:none;">06 | MCP 接入外部工具链：让 AI 真正拥有"双手"</a></p>
<p style="margin-bottom:15px;line-height:1.8;font-size:15px;color:#333;"><a href="https://mp.weixin.qq.com/s/memory-07" style="color:#3b82f6;text-decoration:none;">07 | AI 记住了你是谁：Memory 跨会话记忆实战</a></p>
<div style="border-left:4px solid #22c55e;background:#f0fdf4;padding:12px 16px;margin:15px 0;border-radius:0 8px 8px 0;"><p style="margin:0;color:#166534;font-size:15px;line-height:1.8;">以上文章均可在「金岩讲AI」公众号历史消息中查看。</p></div>
<hr style="border:none;border-top:2px solid #e2e8f0;margin:20px 0;" />'''

# Test just the h1
print(f"h1 only: {'OK' if test(s0[:200], 'h1') else 'FAIL'}")
time.sleep(0.5)

# Test h1 + first p
end = s0.find('</strong></p>') + len('</strong></p>')
print(f"h1 + first p: {'OK' if test(s0[:end], 'h1+p1') else 'FAIL'}")
time.sleep(0.5)

# Test h1 + first 3 links
end = s0.find('</a></p>', s0.find('</a></p>') + 1) + len('</a></p>')
# Find third link end
pos = 0
for _ in range(3):
    pos = s0.find('</a></p>', pos) + len('</a></p>')
print(f"h1 + 3 links: {'OK' if test(s0[:pos], 'h1+3links') else 'FAIL'}")
time.sleep(0.5)

# Test ALL links (up to div)
end = s0.find('<div')
print(f"h1 + all links: {'OK' if test(s0[:end], 'h1+links') else 'FAIL'}")
time.sleep(0.5)

# Test full s0
print(f"Full s0: {'OK' if test(s0, 'full_s0') else 'FAIL'}")
time.sleep(0.5)

# Test with section wrapper
print(f"s0 with section: {'OK' if test(f'<section>{s0}</section>', 's0+sec') else 'FAIL'}")
