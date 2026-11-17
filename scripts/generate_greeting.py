#!/usr/bin/env python3
"""Generate the live time greeting SVG for Hashir's GitHub profile.

The greeting follows Pakistan time (PKT, UTC+5, no DST) — GitHub renders
profile images through its Camo proxy, which hides the visitor's location,
so a per-visitor clock is not possible inside a README. PKT (his time) is
the honest, working version: the banner changes through the day and tells
visitors what time it is where he is.

Periods (PKT):
  morning   05:00-11:59   | afternoon 12:00-16:59
  evening   17:00-20:59   | night     21:00-04:59

Usage: python3 generate_greeting.py [--hour H] [--out PATH]
  --hour forces a period (for testing). Default: current PKT hour.
  --out  output path. Default: <repo-root>/assets/greeting.svg
"""
import argparse
import os
from datetime import datetime, timedelta, timezone

PKT = timezone(timedelta(hours=5))

PERIODS = {
    "morning": {
        "greeting": "Good morning \U0001f44b",
        "sub": "Nowshera, Pakistan \u00b7 PKT",
        "sky_top": "#FF9A8B",
        "sky_bottom": "#FFD194",
        "text": "#4A2C2A",
        "sub_text": "#6B3A2A",
        "sun": "#FFD93D",
        "sun_glow": "#FFE98A",
        "sun_cx": 110,
        "sun_cy": 118,
        "sun_r": 36,
        "body": "sun",
    },
    "afternoon": {
        "greeting": "Good afternoon \U0001f44b",
        "sub": "Nowshera, Pakistan \u00b7 PKT",
        "sky_top": "#36D1DC",
        "sky_bottom": "#5B86E5",
        "text": "#FFFFFF",
        "sub_text": "#EAF6FF",
        "sun": "#FFF176",
        "sun_glow": "#FFF9C4",
        "sun_cx": 110,
        "sun_cy": 62,
        "sun_r": 34,
        "body": "sun",
    },
    "evening": {
        "greeting": "Good evening \U0001f44b",
        "sub": "Nowshera, Pakistan \u00b7 PKT",
        "sky_top": "#FF512F",
        "sky_bottom": "#DD2476",
        "text": "#FFFFFF",
        "sub_text": "#FFE3EE",
        "sun": "#FFC107",
        "sun_glow": "#FFD54F",
        "sun_cx": 110,
        "sun_cy": 128,
        "sun_r": 36,
        "body": "sun",
    },
    "night": {
        "greeting": "Good night \U0001f319",
        "sub": "Nowshera, Pakistan \u00b7 PKT",
        "sky_top": "#0F2027",
        "sky_bottom": "#2C5364",
        "text": "#FFFFFF",
        "sub_text": "#C7D8E0",
        "sun": "#F5F3CE",
        "sun_glow": "#FFFDE7",
        "sun_cx": 110,
        "sun_cy": 78,
        "sun_r": 28,
        "body": "moon",
    },
}


def period_for_hour(hour):
    if 5 <= hour < 12:
        return "morning"
    if 12 <= hour < 17:
        return "afternoon"
    if 17 <= hour < 21:
        return "evening"
    return "night"


def clouds():
    return """
  <g fill="#FFFFFF" opacity="0.85">
    <g>
      <ellipse cx="330" cy="52" rx="52" ry="16"/>
      <ellipse cx="360" cy="44" rx="40" ry="14"/>
      <animateTransform attributeName="transform" type="translate"
        values="-12 0; 12 0; -12 0" dur="26s" repeatCount="indefinite"/>
    </g>
    <g opacity="0.7">
      <ellipse cx="640" cy="150" rx="60" ry="15"/>
      <ellipse cx="672" cy="142" rx="44" ry="13"/>
      <animateTransform attributeName="transform" type="translate"
        values="10 0; -10 0; 10 0" dur="32s" repeatCount="indefinite"/>
    </g>
  </g>"""


def stars():
    spots = [(210, 40), (300, 26), (420, 44), (520, 30), (640, 52),
             (730, 36), (800, 60), (250, 90), (560, 78), (700, 96),
             (360, 84), (470, 20)]
    out = []
    for i, (x, y) in enumerate(spots):
        r = 2.2 if i % 3 else 3.0
        out.append(
            '  <circle cx="%d" cy="%d" r="%.1f" fill="#FFFFFF">\n'
            '    <animate attributeName="opacity" values="0.25;1;0.25" '
            'dur="%.1fs" begin="%.1fs" repeatCount="indefinite"/>\n  </circle>'
            % (x, y, r, 2.0 + (i % 4) * 0.7, (i % 5) * 0.5))
    return "\n".join(out)


def sun_or_moon(p):
    cx, cy, r = p["sun_cx"], p["sun_cy"], p["sun_r"]
    glow = (
        '  <circle cx="%d" cy="%d" r="%d" fill="%s" opacity="0.35">\n'
        '    <animateTransform attributeName="transform" type="translate"'
        ' values="0 0; 0 -6; 0 0" dur="4s" repeatCount="indefinite"/>\n  </circle>\n'
        % (cx, cy, r + 16, p["sun_glow"]))
    if p["body"] == "moon":
        core = (
            '  <circle cx="%d" cy="%d" r="%d" fill="%s">\n'
            '    <animateTransform attributeName="transform" type="translate"'
            ' values="0 0; 0 -6; 0 0" dur="4s" repeatCount="indefinite"/>\n  </circle>\n'
            '  <circle cx="%d" cy="%d" r="%d" fill="%s" opacity="0.9"/>\n'
            % (cx, cy, r, p["sun"], cx + 10, cy - 6, r - 9, p["sky_top"]))
    else:
        core = (
            '  <circle cx="%d" cy="%d" r="%d" fill="%s">\n'
            '    <animateTransform attributeName="transform" type="translate"'
            ' values="0 0; 0 -6; 0 0" dur="4s" repeatCount="indefinite"/>\n  </circle>\n'
            % (cx, cy, r, p["sun"]))
    return glow + core


def build_svg(period):
    p = PERIODS[period]
    deco = stars() if period == "night" else clouds()
    return """<svg xmlns="http://www.w3.org/2000/svg" width="880" height="200" viewBox="0 0 880 200" role="img" aria-label="{greeting} from Pakistan">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{sky_top}"/>
      <stop offset="100%" stop-color="{sky_bottom}"/>
    </linearGradient>
  </defs>
  <rect width="880" height="200" rx="16" fill="url(#sky)"/>
{deco}
{sun}
  <g text-anchor="middle" font-family="Segoe UI, Helvetica, Arial, sans-serif">
    <text x="470" y="98" font-size="46" font-weight="700" fill="{text}" opacity="1">
      {greeting}
      <animate attributeName="opacity" values="0;1" dur="1s" fill="freeze"/>
    </text>
    <text x="470" y="140" font-size="19" font-weight="600" fill="{sub_text}" opacity="1">
      {sub}
      <animate attributeName="opacity" values="0;1" dur="1s" begin="0.3s" fill="freeze"/>
    </text>
  </g>
</svg>
""".format(
        greeting=p["greeting"], sub=p["sub"],
        sky_top=p["sky_top"], sky_bottom=p["sky_bottom"],
        text=p["text"], sub_text=p["sub_text"],
        deco=deco, sun=sun_or_moon(p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hour", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    hour = args.hour if args.hour is not None else datetime.now(PKT).hour
    period = period_for_hour(hour)
    svg = build_svg(period)

    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(here)
    out = args.out or os.path.join(repo_root, "assets", "greeting.svg")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print("hour=%d period=%s -> %s" % (hour, period, out))


if __name__ == "__main__":
    main()
