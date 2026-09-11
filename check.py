#!/usr/bin/env python3
"""Проверка целостности: баланс тегов, CSS-скобки, структура видов."""
import re, sys, subprocess, pathlib
p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else 'vitamins.html')
s = p.read_text(encoding='utf-8')
html = s[:s.rindex('<script>')]
ok = True

for tag in ('div', 'main', 'section', 'article', 'figure', 'nav', 'header', 'footer', 'ul', 'table'):
    o = len(re.findall(r'<%s[\s>]' % tag, html))
    c = len(re.findall(r'</%s>' % tag, html))
    if o != c:
        print(f'  ✗ <{tag}>: открыто {o}, закрыто {c}'); ok = False

css = s[s.index('<style>') + 7:s.index('</style>')]
if css.count('{') != css.count('}'):
    print(f'  ✗ CSS скобки: {css.count("{")} / {css.count("}")}'); ok = False

views = re.findall(r'<div class="view[^"]*" id="view-(\w+)"', html)
if len(views) != 5:
    print(f'  ✗ видов найдено {len(views)}: {views}'); ok = False

body = html[html.index('<main id="content">'):]
depth = 0
for m in re.finditer(r'<(/?)div[\s>]', body):
    depth += -1 if m.group(1) else 1
    if depth < 0:
        print('  ✗ лишний </div> внутри main'); ok = False; break

js = s[s.rindex('<script>') + 8:s.rindex('</script>')]
pathlib.Path('/tmp/_check.js').write_text(js, encoding='utf-8')
r = subprocess.run(['node', '--check', '/tmp/_check.js'], capture_output=True, text=True)
if r.returncode:
    print('  ✗ JS:', r.stderr.strip().split('\n')[0]); ok = False

print('✓ структура цела' if ok else '✗ есть проблемы')
sys.exit(0 if ok else 1)
