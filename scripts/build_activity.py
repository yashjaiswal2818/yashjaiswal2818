# Draws assets/activity.svg: my real GitHub contribution graph in a macOS window, squares popping in.
# Standalone (stdlib only) so a scheduled GitHub Action can refresh it. Usage: python3 build_activity.py [user] [out.svg]
import json, sys, os, urllib.request, datetime
USER = sys.argv[1] if len(sys.argv) > 1 else "yashjaiswal2818"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "activity.svg")
SANS = "-apple-system,BlinkMacSystemFont,'SF Pro Text','Segoe UI',Helvetica,Arial,sans-serif"

req = urllib.request.Request(f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last", headers={"User-Agent": "profile-readme"})
data = json.load(urllib.request.urlopen(req, timeout=30))
days, total = data["contributions"], data["total"]["lastYear"]

# weeks start on Sunday; pad the first column
first = datetime.date.fromisoformat(days[0]["date"])
pad = (first.weekday() + 1) % 7
cells = [None] * pad + days
weeks = [cells[i:i + 7] for i in range(0, len(cells), 7)]

streak = 0
for i in range(len(days) - 1, -1, -1):
    if days[i]["count"] > 0: streak += 1
    elif i != len(days) - 1: break
today = days[-1]["count"]
best_day = max(days, key=lambda d: d["count"])

LEVEL = ["#ebedf0", "#bcd9fb", "#7db7f7", "#3d8ef0", "#1E5FD0"]
CELL, GAP = 13, 3.4
W, H = 960, 306
WX, WY, WW, WH = 24, 14, 912, 278
gx = WX + (WW - len(weeks) * (CELL + GAP) + GAP) / 2
gy = WY + 40 + 84

parts, mon_labels, last_m, last_x = [], [], None, -999
for wi, wk in enumerate(weeks):
    x = gx + wi * (CELL + GAP)
    for di, d in enumerate(wk):
        if d is None: continue
        y = gy + di * (CELL + GAP)
        delay = wi * 0.045 + di * 0.012
        parts.append(f'<rect class="c" style="animation-delay:{delay:.2f}s" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="3" fill="{LEVEL[d["level"]]}"/>')
    m = datetime.date.fromisoformat(next(d for d in wk if d)["date"]).strftime("%b")
    if m != last_m and wi < len(weeks) - 2 and x - last_x >= 44:
        last_x = x
        mon_labels.append(f'<text x="{x:.1f}" y="{gy-8}" font-family="{SANS}" font-size="10.5" fill="#9ca3af">{m}</text>'); last_m = m
for di, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    mon_labels.append(f'<text x="{gx-8:.1f}" y="{gy + di*(CELL+GAP) + 10.5:.1f}" text-anchor="end" font-family="{SANS}" font-size="10" fill="#9ca3af">{lab}</text>')

stat = lambda x, big, small, anchor="start": (f'<text x="{x}" y="{WY+40+34}" text-anchor="{anchor}" font-family="{SANS}" font-size="22" font-weight="800" letter-spacing="-.5" fill="#0a0a0a">{big}</text>'
                                               f'<text x="{x}" y="{WY+40+52}" text-anchor="{anchor}" font-family="{SANS}" font-size="11.5" fill="#6b7280">{small}</text>')
px = gx
legend_x = WX + WW - 30
legend = "".join(f'<rect x="{legend_x - 18*(5-i) - 34:.0f}" y="{WY+WH-27}" width="11" height="11" rx="2.5" fill="{LEVEL[i]}"/>' for i in range(5))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{total} GitHub contributions in the last year, a {streak}-day streak">
<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="125%"><feDropShadow dy="8" stdDeviation="10" flood-color="#0a2a6e" flood-opacity=".16"/></filter>
<clipPath id="cl"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="14"/></clipPath></defs>
<style>
.c{{transform-box:fill-box;transform-origin:center;opacity:0;animation:pop 14s ease-out infinite backwards}}
@keyframes pop{{0%{{opacity:0;transform:scale(.2)}}4%{{opacity:1;transform:scale(1.18)}}6%{{transform:scale(1)}}90%{{opacity:1;transform:scale(1)}}96%,100%{{opacity:0;transform:scale(.6)}}}}
.fire{{animation:fire 1.6s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:bottom center}}
@keyframes fire{{from{{transform:scale(1) rotate(-4deg)}}to{{transform:scale(1.14) rotate(4deg)}}}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}.c{{opacity:1}}}}
</style>
<g filter="url(#sh)"><rect x="{WX}" y="{WY}" width="{WW}" height="{WH}" rx="14" fill="#fff"/></g>
<g clip-path="url(#cl)"><rect x="{WX}" y="{WY}" width="{WW}" height="40" fill="#f6f6f8"/><rect x="{WX}" y="{WY+39}" width="{WW}" height="1" fill="#000" fill-opacity=".07"/></g>
<circle cx="{WX+22}" cy="{WY+20}" r="6.5" fill="#ff5f57" stroke="#000" stroke-opacity=".1"/><circle cx="{WX+42}" cy="{WY+20}" r="6.5" fill="#febc2e" stroke="#000" stroke-opacity=".1"/><circle cx="{WX+62}" cy="{WY+20}" r="6.5" fill="#28c840" stroke="#000" stroke-opacity=".1"/>
<text x="{W/2}" y="{WY+25}" text-anchor="middle" font-family="{SANS}" font-size="13.5" font-weight="600" fill="#262626">git log — {USER}</text>
{stat(gx, f"{total:,}", "contributions in the last year")}
{stat(W/2, f'<tspan class="fire">🔥</tspan> {streak}-day streak' if streak >= 3 else f"{today} today", f"{today} today" if streak >= 3 else "keeping it going", "middle")}
{stat(gx + len(weeks)*(CELL+GAP) - GAP, f"{best_day['count']}", f"best day, {datetime.date.fromisoformat(best_day['date']).strftime('%b %-d')}", "end")}
{''.join(mon_labels)}
{''.join(parts)}
<text x="{legend_x - 18*5 - 40:.0f}" y="{WY+WH-18}" text-anchor="end" font-family="{SANS}" font-size="10.5" fill="#9ca3af">less</text>{legend}<text x="{legend_x:.0f}" y="{WY+WH-18}" font-family="{SANS}" font-size="10.5" fill="#9ca3af">more</text>
</svg>'''
os.makedirs(os.path.dirname(OUT), exist_ok=True); open(OUT, "w").write(svg)
print(f"{total} contributions, {streak}-day streak, {len(weeks)} weeks, {round(len(svg)/1024,1)} KB")
