#!/usr/bin/env python3
"""Собирает сайт из фрагмента vitamins.html: полный HTML-документ + PWA-обвязка."""
import re, shutil, hashlib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC  = ROOT / "src" / "vitamins.html"
OUT  = ROOT
frag = SRC.read_text(encoding="utf-8")

title = re.search(r"<title>(.*?)</title>", frag).group(1)
links = re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', frag)
body  = frag
body  = re.sub(r"<title>.*?</title>\n?", "", body, count=1)
for l in links:
    body = body.replace(l + "\n", "", 1)

head = f"""<!doctype html>
<html lang="ru" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="Курс, справочник и тренажёр по витаминам: формы, дозировки, клинические кейсы и интервальное повторение.">
<meta name="theme-color" content="#F6F7F9" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#101314" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Витамины">
<meta name="format-detection" content="telephone=no">
<link rel="manifest" href="./manifest.webmanifest">
<link rel="apple-touch-icon" href="./icons/apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="192x192" href="./icons/icon-192.png">
{chr(10).join(links)}
</head>
<body>
"""
(OUT / "index.html").write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")

ver = hashlib.sha1((head + body).encode()).hexdigest()[:10]
sw = (ROOT / "src" / "sw.js").read_text(encoding="utf-8").replace("__VERSION__", ver)
(OUT / "sw.js").write_text(sw, encoding="utf-8")
print(f"index.html собран · версия кэша {ver}")
