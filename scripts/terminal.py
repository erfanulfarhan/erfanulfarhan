"""The two terminal windows on the profile README.

  whoami.svg         `whoami` typed at a prompt; the ASCII portrait prints
                     itself row by row beside a neofetch-style card
  contributions.svg  `./contributions.sh` typed; the year's calendar sweeps in
                     cell by cell, with the totals underneath

Both are redrawn every day from the same data as the other graphics, so the
card's numbers and the calendar stay current. The portrait comes from
data/portrait.txt (scripts/make_portrait.py), drawn once from a photo.

Motion is CSS inside the SVG. GitHub strips scripts from a README but plays an
<img> SVG's own animations, and CSS, unlike SMIL, can be switched off: anyone
whose system asks for reduced motion gets the finished frame at once. Every
element's resting state is its final state; the animations only start it
somewhere else.

The windows stay dark in GitHub's light theme too, as a terminal would.
"""
import html
from datetime import date

W = 860                    # README width; both windows share it
M = 10                     # margin, so the shadow is not clipped
WIN_W = W - 2 * M
BAR = 34                   # title bar
PAD = 22

BG = "#0d1117"
CHROME = "#161b22"
EDGE = "#30363d"
INK = "#c9d1d9"
BRIGHT = "#f0f6fc"
DIM = "#8b949e"
USER = "#7ee787"           # user@host, as zsh colours it
PATH = "#79c0ff"
KEY = "#79c0ff"
GREENS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
LEVEL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
         "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
PALETTE = [["#484f58", "#ff7b72", "#3fb950", "#d29922", "#58a6ff", "#bc8cff", "#39c5cf", "#b1bac4"],
           ["#6e7681", "#ffa198", "#56d364", "#e3b341", "#79c0ff", "#d2a8ff", "#56d4dd", "#f0f6fc"]]
MON = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

FS = 14.0                  # prompt lines
CW = FS * 0.6              # JetBrains Mono advances exactly 0.6 em
USER_HOST, PROMPT_PATH = "farhan@github", "~"
PROMPT_W = len(f"{USER_HOST} {PROMPT_PATH} $ ") * CW


def esc(t):
    return html.escape(t, quote=False)


def css(fonts, extra=""):
    return ("<style>" + fonts +
            "text{font-family:JBMono,ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}"
            ".ty{transform-box:fill-box;transform-origin:100% 50%}"
            ".pp{transform-box:fill-box;transform-origin:50% 50%}"
            "@keyframes type{to{transform:scaleX(0)}}"
            "@keyframes mv{to{transform:translateX(var(--d))}}"
            "@keyframes blink{50%{opacity:0}}"
            "@keyframes gone{to{opacity:0}}"
            "@keyframes rise{from{opacity:0;transform:translateY(5px)}}"
            "@keyframes pop{from{opacity:0;transform:scale(.25)}}"
            "@keyframes pulse{0%,100%{opacity:.15}50%{opacity:1}}"
            "@keyframes on{from,to{opacity:.85}}"
            ".pp{animation:pop .3s ease-out both}"
            + "".join(f".l{i}{{fill:{c}}}" for i, c in enumerate(GREENS)) +
            ".l0{stroke:#fff;stroke-opacity:.05}"
            + extra +
            "@media (prefers-reduced-motion:reduce){*{animation:none!important}.cv{display:none}}"
            "</style>")


def frame(h, title, fonts, extra_css=""):
    """The SVG head and an empty window: shadow, body, title bar, three lights."""
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">',
        css(fonts, extra_css),
        '<defs><filter id="sh" x="-5%" y="-5%" width="110%" height="115%">'
        '<feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#010409" flood-opacity=".35"/>'
        '</filter></defs>',
        f'<rect x="{M}" y="{M}" width="{WIN_W}" height="{h - 2 * M}" rx="12" fill="#010409" filter="url(#sh)"/>',
        f'<rect x="{M}" y="{M}" width="{WIN_W}" height="{h - 2 * M}" rx="12" fill="{BG}"/>',
        f'<path d="M{M} {M + BAR}V{M + 12}a12 12 0 0 1 12-12H{M + WIN_W - 12}a12 12 0 0 1 12 12V{M + BAR}Z" '
        f'fill="{CHROME}"/>',
        f'<line x1="{M}" y1="{M + BAR}" x2="{M + WIN_W}" y2="{M + BAR}" stroke="{EDGE}"/>',
        f'<rect x="{M + .5}" y="{M + .5}" width="{WIN_W - 1}" height="{h - 2 * M - 1}" rx="11.5" '
        f'fill="none" stroke="{EDGE}"/>',
        "".join(f'<circle cx="{M + 20 + i * 18}" cy="{M + BAR / 2}" r="6" fill="{c}"/>'
                for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840"))),
        f'<text x="{W / 2}" y="{M + BAR / 2 + 4.5}" font-size="12.5" fill="{DIM}" '
        f'text-anchor="middle">{esc(title)}</text>',
    ]


def prompt(x, y, cmd, t0, per=0.07, cursor_after=None):
    """`user@host ~ $ cmd`, the command typed a character at a time.

    Returns the markup and the time the typing ends. A cover in the window's
    colour shrinks off the command in steps; a block cursor steps along with
    it, blinks while it waits, and goes when Enter is "pressed".
    """
    n = len(cmd)
    dur = n * per
    cx = x + PROMPT_W
    h = FS * 1.35
    top = y - FS * 1.02
    parts = [f'<text x="{x}" y="{y}" font-size="{FS}" xml:space="preserve">'
             f'<tspan fill="{USER}" font-weight="600">{USER_HOST}</tspan> '
             f'<tspan fill="{PATH}" font-weight="600">{PROMPT_PATH}</tspan> '
             f'<tspan fill="{INK}">$ </tspan><tspan fill="{BRIGHT}">{esc(cmd)}</tspan></text>']
    if n:
        parts.append(f'<rect class="cv ty" x="{cx:.1f}" y="{top:.1f}" width="{n * CW:.1f}" height="{h:.1f}" '
                     f'fill="{BG}" style="animation:type {dur:.2f}s steps({n},end) {t0:.2f}s forwards,'
                     f'gone .01s {t0 + dur:.2f}s forwards"/>')   # WebKit holds steps() one short
    end = t0 + dur
    gone = cursor_after if cursor_after is not None else end + 0.25
    parts.append(f'<rect class="cv" x="{cx:.1f}" y="{top + 1:.1f}" width="{CW:.1f}" height="{h - 2:.1f}" '
                 f'fill="{INK}" style="--d:{n * CW:.1f}px;animation:blink 1s steps(1) infinite,'
                 f'mv {max(dur, .01):.2f}s steps({max(n, 1)},end) {t0:.2f}s forwards,'
                 f'gone .01s {gone:.2f}s forwards"/>')
    return "".join(parts), end


def final_prompt(x, y, t):
    """The prompt the window ends on, with a cursor that keeps blinking."""
    cx = x + PROMPT_W
    return (f'<g style="animation:rise .3s ease-out {t:.2f}s both">'
            f'<text x="{x}" y="{y}" font-size="{FS}" xml:space="preserve">'
            f'<tspan fill="{USER}" font-weight="600">{USER_HOST}</tspan> '
            f'<tspan fill="{PATH}" font-weight="600">{PROMPT_PATH}</tspan> '
            f'<tspan fill="{INK}">$</tspan></text>'
            f'<rect x="{cx:.1f}" y="{y - FS * 1.02 + 1:.1f}" width="{CW:.1f}" height="{FS * 1.35 - 2:.1f}" '
            f'fill="{INK}" style="animation:blink 1.1s steps(1) infinite"/></g>')


def age(created, today):
    """'4 years, 3 months': whole months since the account was made."""
    c = date.fromisoformat(created[:10])
    months = (today.year - c.year) * 12 + today.month - c.month - (today.day < c.day)
    y, m = divmod(max(months, 0), 12)
    bits = ([f"{y} year{'s' * (y != 1)}"] if y else []) + ([f"{m} month{'s' * (m != 1)}"] if m else [])
    return ", ".join(bits) or "new"


# ------------------------------------------------------------------ whoami

PORTRAIT_W = 334           # px; the font size follows from the portrait's column count
PRINT_PER_CHAR = 0.0015    # seconds; the whole bust prints in about three
INFO_FS = 13.5
INFO_LH = 21.5
GAP = 30


def draw_whoami(s, portrait, fonts, today):
    """Prompt, portrait and card, then the prompt again."""
    cols = max(len(r) for r in portrait)
    pfs = PORTRAIT_W / (cols * 0.6)            # font size that fits the columns exactly
    plh = pfs * 1.2
    px = M + PAD
    py = M + BAR + 30                          # prompt baseline
    top = py + 22                              # content top
    ph = len(portrait) * plh

    langs = " · ".join(n for n, _ in s["card_langs"]) or "nothing public yet"
    rows = [("Name", "Erfanul Hakim Farhan"),
            ("Role", "AI and automation developer"),
            ("Location", "Dhaka, Bangladesh"),
            ("Uptime", f"{age(s['created'], today)} on GitHub"),
            ("Repos", f"{s['public_repos']} public"),
            ("Languages", langs),
            ("Stack", "React · Next.js · Electron · FastAPI"),
            ("AI", "Anthropic · Gemini · Groq · Ollama"),
            ("Shipped", "Lens · exam-toolkit · sitesage"),
            ("Activity", f"{s['total']} contributions this year"),
            ("Site", "erfanulfarhan.vercel.app")]
    info_h = (2 + len(rows) + 1 + 2) * INFO_LH
    body = max(ph, info_h)
    ptop = top + (body - ph) / 2               # the shorter of the two sits centred beside the other
    end_y = top + body + 30
    H = int(end_y + 24 + M)

    p = frame(H, f"{USER_HOST}: ~", fonts)
    cmd, typed = prompt(px, py, "whoami", 0.55)
    p.append(cmd)

    # The portrait prints like a terminal printing a file: a row at a time,
    # over only the characters it has, one cursor tracing the bust downwards.
    pcw = pfs * 0.6
    t_row0 = typed + 0.20
    t = t_row0
    for i, row in enumerate(portrait):
        y = ptop + i * plh
        p.append(f'<text x="{px}" y="{y + plh * 0.8:.1f}" font-size="{pfs:.2f}" fill="{INK}" '
                 f'xml:space="preserve">{esc(row)}</text>')
    for i, row in enumerate(portrait):
        if not row.strip():
            continue
        first = len(row) - len(row.lstrip())
        x0, wr = px + first * pcw - 0.5, (len(row) - first) * pcw + 1
        y = ptop + i * plh
        dur = max(0.03, (len(row) - first) * PRINT_PER_CHAR)
        p.append(f'<rect class="cv ty" x="{x0:.1f}" y="{y:.1f}" width="{wr:.1f}" height="{plh + .4:.1f}" '
                 f'fill="{BG}" style="animation:type {dur:.3f}s linear {t:.3f}s forwards"/>')
        p.append(f'<rect class="cv" x="{x0:.1f}" y="{y + .5:.1f}" width="{pcw:.1f}" height="{plh - 1:.1f}" '
                 f'fill="{INK}" opacity="0" style="--d:{wr - pcw:.1f}px;animation:mv {dur:.3f}s linear '
                 f'{t:.3f}s forwards,on {dur:.3f}s linear {t:.3f}s"/>')
        t += dur * 0.7                         # the next row starts as this one finishes
    t_printed = t + 0.1

    # the card, a line at a time
    ix = px + PORTRAIT_W + GAP
    iy = top + (body - info_h) / 2 + INFO_FS
    t_line0, line_gap = t_row0 + 0.15, 0.11
    head = "erfanulfarhan@github"
    lines = [f'<tspan fill="{USER}" font-weight="600">erfanulfarhan</tspan><tspan fill="{INK}">@</tspan>'
             f'<tspan fill="{USER}" font-weight="600">github</tspan>',
             f'<tspan fill="{DIM}">{"-" * len(head)}</tspan>']
    for k, v in rows:
        lines.append(f'<tspan fill="{KEY}" font-weight="600">{esc(k)}</tspan>'
                     f'<tspan fill="{DIM}">{" " * (11 - len(k))}</tspan><tspan fill="{INK}">{esc(v)}</tspan>')
    for j, ln in enumerate(lines):
        p.append(f'<g style="animation:rise .4s ease-out {t_line0 + j * line_gap:.2f}s both">'
                 f'<text x="{ix}" y="{iy + j * INFO_LH:.1f}" font-size="{INFO_FS}" xml:space="preserve">'
                 f'{ln}</text></g>')
    by = iy + (len(lines) + 0.6) * INFO_LH
    bw, bh = INFO_FS * 0.6 * 3, INFO_LH * 0.78
    for r, colours in enumerate(PALETTE):
        tc = t_line0 + (len(lines) + r) * line_gap
        p.append(f'<g style="animation:rise .4s ease-out {tc:.2f}s both">'
                 + "".join(f'<rect x="{ix + c * bw:.1f}" y="{by - INFO_FS + r * bh:.1f}" width="{bw:.1f}" '
                           f'height="{bh:.1f}" fill="{col}"/>' for c, col in enumerate(colours)) + "</g>")

    t_end = max(t_printed, tc + 0.4) + 0.15
    p.append(final_prompt(px, end_y, t_end))
    p.append("</svg>")
    return "".join(p)


# ------------------------------------------------------------ contributions

CELL, PITCH = 11.0, 14.0


def draw_contributions(s, fonts, today):
    """The calendar as GitHub draws it, swept in diagonally, totals beneath."""
    weeks = s["weeks"]
    px = M + PAD
    py = M + BAR + 30
    gx = px + 34                               # after the weekday labels
    head_y = py + 30
    month_y = head_y + 26
    gy = month_y + 8
    foot_y = gy + 7 * PITCH + 24
    end_y = foot_y + 22 * 2 + 18
    H = int(end_y + 24 + M)

    p = frame(H, f"{USER_HOST}: ~", fonts)
    cmd, typed = prompt(px, py, "./contributions.sh", 0.5, per=0.05)
    p.append(cmd)

    t_out = typed + 0.2
    first, last = weeks[0][0]["date"], weeks[-1][-1]["date"]
    span = f"{pretty_long(first)} to {pretty_long(last)}"
    p.append(f'<g style="animation:rise .35s ease-out {t_out:.2f}s both">'
             f'<text x="{px}" y="{head_y}" font-size="{FS}" xml:space="preserve">'
             f'<tspan fill="{BRIGHT}" font-weight="600">{s["total"]}</tspan>'
             f'<tspan fill="{INK}"> contributions in the last year</tspan></text>'
             f'<text x="{M + WIN_W - PAD}" y="{head_y}" font-size="12" fill="{DIM}" '
             f'text-anchor="end">{span}</text></g>')

    # month labels, weekday labels
    t_grid = t_out + 0.25
    last_m, last_x = None, -99.0
    labels = []
    for i, w in enumerate(weeks):
        m = int(w[0]["date"][5:7])
        x = gx + i * PITCH
        if m != last_m and x - last_x >= 30 and i < len(weeks) - 1:
            labels.append(f'<text x="{x:.1f}" y="{month_y}" font-size="11" fill="{DIM}">{MON[m - 1]}</text>')
            last_x = x
        last_m = m
    for r, lab in ((1, "mon"), (3, "wed"), (5, "fri")):
        labels.append(f'<text x="{gx - 8}" y="{gy + r * PITCH + CELL - 2:.1f}" font-size="10.5" fill="{DIM}" '
                      f'text-anchor="end">{lab}</text>')
    p.append(f'<g style="animation:rise .35s ease-out {t_grid:.2f}s both">' + "".join(labels) + "</g>")

    # the cells: a diagonal sweep, left to right and top to bottom
    today_cell = None
    for i, w in enumerate(weeks):
        for d in w:
            r = d["weekday"]
            x, y = gx + i * PITCH, gy + r * PITCH
            lv = LEVEL.get(d.get("contributionLevel"), 0)
            t = t_grid + i * 0.017 + r * 0.035
            p.append(f'<rect class="pp l{lv}" x="{x:.1f}" y="{y:.1f}" width="{CELL}" height="{CELL}" rx="2.5" '
                     f'style="animation-delay:{t:.2f}s"/>')
            if d["date"] == today.isoformat():
                today_cell = (x, y)
    t_cells = t_grid + (len(weeks) - 1) * 0.017 + 6 * 0.035 + 0.3
    if today_cell:                              # today, breathing: the graph is live
        x, y = today_cell
        p.append(f'<rect x="{x - 2:.1f}" y="{y - 2:.1f}" width="{CELL + 4}" height="{CELL + 4}" rx="4" '
                 f'fill="none" stroke="{GREENS[4]}" stroke-width="1.5" opacity=".6" '
                 f'style="animation:rise .3s {t_cells:.2f}s both,pulse 2.4s ease-in-out {t_cells + .3:.2f}s infinite"/>')

    # the totals, and a legend so the colour is never the only cue
    best = s["best_day"]
    stats = [("active days", f'{s["active"]}'),
             ("best day", f'{best["count"]} on {pretty_short(best["date"])}' if best["count"] else "none yet"),
             ("longest streak", f'{s["longest"]["length"]}d'),
             ("current", f'{s["current"]["length"]}d')]
    bits = []
    for k, v in stats:
        bits.append(f'<tspan fill="{DIM}">{k} </tspan><tspan fill="{BRIGHT}" font-weight="600">{esc(v)}</tspan>'
                    f'<tspan fill="{DIM}">   </tspan>')
    p.append(f'<g style="animation:rise .35s ease-out {t_cells:.2f}s both">'
             f'<text x="{px}" y="{foot_y}" font-size="12.5" xml:space="preserve">{"".join(bits)}</text>')
    lx = M + WIN_W - PAD
    sq_end = lx - 4 * 11 * 0.6 - 7             # leave room for "more"
    sq_start = sq_end - (5 * (CELL + 3) - 3)
    p.append(f'<text x="{sq_start - 6:.1f}" y="{foot_y}" font-size="11" fill="{DIM}" text-anchor="end">less</text>')
    p.append("".join(f'<rect x="{sq_start + k * (CELL + 3):.1f}" y="{foot_y - CELL + 1:.1f}" width="{CELL}" '
                     f'height="{CELL}" rx="2.5" fill="{GREENS[k]}"/>' for k in range(5)))
    p.append(f'<text x="{lx}" y="{foot_y}" font-size="11" fill="{DIM}" text-anchor="end">more</text>')
    p.append(f'<text x="{px}" y="{foot_y + 22}" font-size="12" fill="{DIM}" xml:space="preserve">'
             f'# redrawn {pretty_long(today.isoformat())} by a scheduled GitHub Action</text></g>')

    p.append(final_prompt(px, end_y, t_cells + 0.4))
    p.append("</svg>")
    return "".join(p)


def pretty_short(iso):
    d = date.fromisoformat(iso)
    return f"{MON[d.month - 1]} {d.day}"


def pretty_long(iso):
    d = date.fromisoformat(iso)
    return f"{MON[d.month - 1]} {d.day}, {d.year}"
