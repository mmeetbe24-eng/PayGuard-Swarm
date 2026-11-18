"""
Shared visual theme for the PayGuard Swarm Streamlit frontend.

Light editorial look: soft grey canvas, white framed sheets, deep navy accents,
sky-blue and sand panels, heavy ink section dividers, pill buttons and chips.
Presentation only - no business logic lives here.
"""
import re
import html as _html
import streamlit as st

# ---------------------------------------------------------------------------
# Emoji scrubbing (applied to any text rendered in the UI, including strings
# that originate from backend agents, so the interface stays emoji-free).
# ---------------------------------------------------------------------------
_EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"   # pictographs, emoticons, transport, symbols ext.
    "☀-➿"           # misc symbols & dingbats (includes check/cross marks)
    "⬀-⯿"           # misc symbols & arrows (stars, squares)
    "⌀-⏿"           # misc technical (hourglass, stopwatch)
    "ℹ"                  # information source
    "️︎‍"      # variation selectors / zero-width joiner
    "]+"
)


def clean(text) -> str:
    """Strip emoji and tidy leftover whitespace."""
    if text is None:
        return ""
    out = _EMOJI_RE.sub("", str(text))
    out = re.sub(r"[ \t]{2,}", " ", out)
    return out.strip()


def esc(text) -> str:
    """Clean + HTML-escape for safe interpolation into markup (single line, so it
    can never break out of an HTML block in Streamlit's markdown renderer)."""
    return _html.escape(re.sub(r"\s*\n\s*", " ", clean(text)))


# Map legacy accent colours (some arrive from backend step payloads) onto theme tones.
_TONE_BY_HEX = {
    "#EF4444": "red",
    "#10B981": "navy",
    "#34D399": "navy",
    "#F59E0B": "sand",
    "#FBBF24": "sand",
    "#38BDF8": "sky",
    "#A78BFA": "sky",
}


def tone_for(hex_color: str, default: str = "sky") -> str:
    return _TONE_BY_HEX.get(str(hex_color).upper(), default)


ARROW_SVG = (
    '<svg class="pg-arrow" viewBox="0 0 24 24" width="18" height="18" fill="none" '
    'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M7 17L17 7"/><path d="M8 7h9v9"/></svg>'
)
CHECK_SVG = (
    '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" '
    'stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>'
)
CROSS_SVG = (
    '<svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" '
    'stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>'
)


# ---------------------------------------------------------------------------
# Small HTML builders
# ---------------------------------------------------------------------------
def chip(text, tone: str = "outline") -> str:
    return f'<span class="pg-chip pg-chip-{tone}">{esc(text)}</span>'


def section(title: str, eyebrow: str = "", lede: str = "", title_accent: str = "") -> None:
    """Section heading: small letter-spaced eyebrow, large tight headline, muted lede."""
    eb = f'<div class="pg-eyebrow"><span class="pg-dot"></span>{esc(eyebrow)}</div>' if eyebrow else ""
    accent = f'<br><span class="pg-accent">{esc(title_accent)}</span>' if title_accent else ""
    ld = f'<p class="pg-lede">{lede}</p>' if lede else ""
    st.markdown(
        f'<div class="pg-section">{eb}<h2 class="pg-h2">{esc(title)}{accent}</h2>{ld}</div>',
        unsafe_allow_html=True,
    )


def divider() -> None:
    st.markdown('<div class="pg-rule"></div>', unsafe_allow_html=True)


def page_hero(eyebrow: str, line1: str, line2: str, lede: str) -> None:
    st.markdown(
        f"""
        <div class="pg-hero-solo">
            <div class="pg-eyebrow"><span class="pg-dot"></span>{esc(eyebrow)}</div>
            <h1 class="pg-display">{esc(line1)}<br><span class="pg-accent">{esc(line2)}</span></h1>
            <p class="pg-lede pg-lede-lg">{esc(lede)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(eyebrow: str, title: str, body_html: str, tone: str = "white", footer: str = "", index: str = "") -> str:
    """Service-style panel: eyebrow, heading, body, thin rule, footer + arrow."""
    eb = f"{esc(index)} / {esc(eyebrow)}" if index else esc(eyebrow)
    foot = (
        f'<div class="pg-card-foot"><span>{footer}</span>{ARROW_SVG}</div>' if footer else ""
    )
    return (
        f'<div class="pg-card pg-tone-{tone}">'
        f'<div class="pg-card-eyebrow">{eb}</div>'
        f'<h3 class="pg-card-title">{esc(title)}</h3>'
        f'<div class="pg-card-body">{body_html}</div>{foot}</div>'
    )


def card_row(cards_html: list, compact: bool = False) -> None:
    """Framed row of panels separated by heavy ink dividers; reflows by container width."""
    cls = f"pg-card-row cols-{min(len(cards_html), 5)}" + (" compact" if compact else "")
    st.markdown(f'<div class="pg-cq"><div class="{cls}">{"".join(cards_html)}</div></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Global stylesheet
# ---------------------------------------------------------------------------
_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@500;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --pg-canvas: #F4F5F7;
    --pg-surface: #FFFFFF;
    --pg-ink: #12172B;
    --pg-body: #3B4255;
    --pg-muted: #5F6779;
    --pg-navy: #263C8A;
    --pg-navy-deep: #1D2F6F;
    --pg-sky: #9EC5F6;
    --pg-sky-soft: #EAF2FD;
    --pg-sand: #E8DFCC;
    --pg-sand-soft: #F4EFE4;
    --pg-red: #A8322B;
    --pg-red-soft: #F8E9E7;
    --pg-line: #DADFE7;
    --pg-frame: #12172B;
    --pg-radius: 22px;
    --pg-display: 'Manrope', 'Inter', system-ui, sans-serif;
    --pg-text: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ---------- Base ---------- */
html, body, .stApp, [class*="css"] {
    font-family: var(--pg-text) !important;
    color: var(--pg-ink);
}
.stApp { background: var(--pg-canvas) !important; }
header[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stDecoration"] { display: none !important; }

.block-container {
    max-width: 1320px !important;
    padding: 2.25rem 3.25rem 4rem 3.25rem !important;
    margin-top: 1.25rem !important;
    margin-bottom: 2rem !important;
    background: var(--pg-surface);
    border: 2px solid var(--pg-frame);
    border-radius: var(--pg-radius);
}
@media (max-width: 760px) {
    .block-container { padding: 1.5rem 1rem 3rem 1rem !important; border-radius: 16px; }
}

p, li, label, .stMarkdown { color: var(--pg-body); line-height: 1.65; }
strong, b { color: var(--pg-ink); font-weight: 600; }
a { color: var(--pg-navy) !important; }

h1, h2, h3, h4, h5, h6,
[data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4 {
    font-family: var(--pg-display) !important;
    color: var(--pg-ink) !important;
    letter-spacing: -0.03em !important;
    font-weight: 800 !important;
}
[data-testid="stMarkdownContainer"] h2 { font-size: 2rem !important; line-height: 1.1 !important; }
[data-testid="stMarkdownContainer"] h3 { font-size: 1.45rem !important; }
[data-testid="stMarkdownContainer"] h4 { font-size: 1.15rem !important; letter-spacing: -0.02em !important; }

code, pre, .stCode, [data-testid="stCode"] * { font-family: 'JetBrains Mono', monospace !important; }
[data-testid="stMarkdownContainer"] code {
    background: var(--pg-sky-soft) !important; color: var(--pg-navy-deep) !important;
    border-radius: 6px; padding: 1px 6px; font-size: 0.84em;
}
[data-testid="stCode"], .stCode {
    border: 1px solid var(--pg-line) !important; border-radius: 14px !important; overflow: hidden;
}
[data-testid="stCode"] pre { background: var(--pg-canvas) !important; }

/* Section rules: heavy ink line spanning the framed sheet */
hr, [data-testid="stMarkdownContainer"] hr {
    border: none !important;
    border-top: 2px solid var(--pg-frame) !important;
    margin: 2.75rem -3.25rem !important;
    opacity: 1 !important;
}
.pg-rule { border-top: 2px solid var(--pg-frame); margin: 2.75rem -3.25rem; }
@media (max-width: 760px) {
    hr, [data-testid="stMarkdownContainer"] hr, .pg-rule { margin: 2rem -1rem !important; }
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"] {
    background: var(--pg-surface) !important;
    border-right: 2px solid var(--pg-frame) !important;
}
section[data-testid="stSidebar"] hr { margin: 1.5rem 0 !important; border-top: 1px solid var(--pg-line) !important; }
section[data-testid="stSidebar"] h1 { font-size: 1.6rem !important; }
section[data-testid="stSidebar"] h3 {
    font-family: var(--pg-text) !important; font-size: 0.72rem !important; font-weight: 600 !important;
    letter-spacing: 0.18em !important; text-transform: uppercase; color: var(--pg-navy) !important;
}
section[data-testid="stSidebar"] li { font-size: 0.86rem; margin-bottom: 0.25rem; }

/* ---------- Typography helpers ---------- */
.pg-eyebrow {
    display: flex; align-items: center; gap: 10px;
    font-family: var(--pg-text); font-size: 0.74rem; font-weight: 600;
    letter-spacing: 0.2em; text-transform: uppercase; color: var(--pg-navy);
    margin-bottom: 1rem;
}
.pg-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--pg-navy); display: inline-block; }
.pg-display {
    font-family: var(--pg-display) !important; font-weight: 800 !important;
    font-size: clamp(2.4rem, 5vw, 4.1rem) !important; line-height: 1.02 !important;
    letter-spacing: -0.045em !important; color: var(--pg-ink) !important; margin: 0 0 1.25rem 0 !important;
    padding: 0 !important;
}
.pg-accent { color: var(--pg-navy) !important; }
.pg-h2 {
    font-family: var(--pg-display) !important; font-weight: 800 !important;
    font-size: clamp(1.7rem, 3vw, 2.35rem) !important; line-height: 1.08 !important;
    letter-spacing: -0.035em !important; color: var(--pg-ink) !important; margin: 0 0 0.6rem 0 !important; padding: 0 !important;
}
.pg-lede { color: var(--pg-muted) !important; font-size: 1.02rem; line-height: 1.7; max-width: 760px; margin: 0; }
.pg-lede-lg { font-size: 1.15rem; }
.pg-section { margin: 0.25rem 0 1.5rem 0; }
.pg-hero-solo { padding: 1.25rem 0 0.5rem 0; }
.pg-muted { color: var(--pg-muted) !important; }
.pg-small { font-size: 0.85rem; }

/* ---------- Brand bar ---------- */
.pg-brand { display: flex; flex-direction: column; line-height: 1; padding-top: 2px; }
.pg-brand-word {
    font-family: var(--pg-display); font-weight: 800; font-size: 2rem; letter-spacing: -0.06em; color: var(--pg-navy);
}
.pg-brand-word span { color: var(--pg-ink); }
.pg-brand-sub {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.3em; text-transform: uppercase; color: var(--pg-navy); margin-top: 6px;
}

/* ---------- Hero split ---------- */
.pg-hero {
    display: grid; grid-template-columns: 1.15fr 1fr;
    border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); overflow: hidden; margin: 0.5rem 0 0.5rem 0;
}
.pg-hero-left { padding: 2.75rem 2.75rem 2.5rem 2.75rem; background: var(--pg-surface); position: relative; }
.pg-hero-left::before {
    content: ""; position: absolute; top: 18px; left: 18px; width: 22px; height: 22px;
    border-top: 1.5px solid var(--pg-muted); border-left: 1.5px solid var(--pg-muted);
}
.pg-hero-right { display: grid; grid-template-columns: 1fr 1fr; border-left: 2px solid var(--pg-frame); }
.pg-kpi { padding: 1.6rem 1.6rem 1.4rem 1.6rem; display: flex; flex-direction: column; justify-content: space-between; min-height: 170px; }
.pg-kpi:nth-child(1) { border-right: 2px solid var(--pg-frame); border-bottom: 2px solid var(--pg-frame); }
.pg-kpi:nth-child(2) { border-bottom: 2px solid var(--pg-frame); }
.pg-kpi:nth-child(3) { border-right: 2px solid var(--pg-frame); }
.pg-kpi-label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; }
.pg-kpi-value { font-family: var(--pg-display); font-weight: 800; font-size: 2.5rem; letter-spacing: -0.04em; line-height: 1; margin: 0.9rem 0 0.5rem 0; }
.pg-kpi-note { font-size: 0.85rem; }
@media (max-width: 900px) {
    .pg-hero { grid-template-columns: 1fr; }
    .pg-hero-right { border-left: none; border-top: 2px solid var(--pg-frame); }
    .pg-hero-left { padding: 2rem 1.4rem; }
}

/* ---------- Tones ---------- */
.pg-tone-navy  { background: var(--pg-navy) !important; color: #E7ECFA !important; }
.pg-tone-navy *  { color: #E7ECFA !important; }
.pg-tone-navy .pg-card-title, .pg-tone-navy .pg-kpi-value, .pg-tone-navy strong { color: #FFFFFF !important; }
.pg-tone-sky   { background: var(--pg-sky) !important; }
.pg-tone-sky *   { color: var(--pg-navy-deep) !important; }
.pg-tone-sand  { background: var(--pg-sand) !important; }
.pg-tone-sand *  { color: var(--pg-ink) !important; }
.pg-tone-sand .pg-card-body, .pg-tone-sand .pg-card-body * { color: var(--pg-body) !important; }
.pg-tone-white { background: var(--pg-surface) !important; }
.pg-tone-white .pg-card-eyebrow, .pg-tone-white .pg-kpi-label { color: var(--pg-navy) !important; }
.pg-tone-white .pg-kpi-value { color: var(--pg-navy) !important; }
.pg-tone-red   { background: var(--pg-red-soft) !important; }
.pg-tone-red .pg-card-eyebrow, .pg-tone-red .pg-card-title { color: var(--pg-red) !important; }

/* ---------- Cards / panels ---------- */
.pg-cq { container-type: inline-size; margin-bottom: 1rem; }
.pg-card-row {
    display: grid; grid-template-columns: 1fr; gap: 2px; background: var(--pg-frame);
    border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); overflow: hidden;
}
.pg-card-row > .pg-card { border: none !important; border-radius: 0 !important; margin: 0 !important; }
.pg-card-row.compact > .pg-card { padding: 1.3rem 1.3rem 1.1rem 1.3rem; }
.pg-card-row.compact .pg-card-title { font-size: 1.2rem !important; }
.pg-card-row.compact .pg-price { font-size: 1.7rem; }
@container (min-width: 440px) { .pg-card-row.cols-2, .pg-card-row.cols-4 { grid-template-columns: repeat(2, 1fr); } }
@container (min-width: 600px) { .pg-card-row.cols-3 { grid-template-columns: repeat(3, 1fr); } }
@container (min-width: 820px) { .pg-card-row.cols-4 { grid-template-columns: repeat(4, 1fr); } }
@container (min-width: 700px) { .pg-card-row.cols-5 { grid-template-columns: repeat(5, 1fr); } }
.pg-card { border-radius: 0; border: none; border-right: 2px solid var(--pg-frame); }
.pg-card-row > .pg-card:last-child { border-right: none; }
@media (max-width: 760px) {
    .pg-card-row > .pg-card { border-right: none; border-bottom: 2px solid var(--pg-frame); }
    .pg-card-row > .pg-card:last-child { border-bottom: none; }
}
.pg-card {
    padding: 1.75rem 1.75rem 1.4rem 1.75rem; display: flex; flex-direction: column;
    border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); margin-bottom: 1rem; height: 100%;
}
.pg-card-eyebrow { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; margin-bottom: 1.25rem; color: var(--pg-muted); }
.pg-card-title {
    font-family: var(--pg-display) !important; font-weight: 800 !important; font-size: 1.55rem !important;
    letter-spacing: -0.035em !important; line-height: 1.12 !important; margin: 0 0 0.75rem 0 !important; padding: 0 !important; color: var(--pg-ink);
}
.pg-card-body { font-size: 0.94rem; line-height: 1.65; flex: 1; color: var(--pg-body); }
.pg-card-body p { margin: 0 0 0.6rem 0; }
.pg-card-body ul { margin: 0.25rem 0 0 1.1rem; padding: 0; }
.pg-card-foot {
    display: flex; align-items: center; justify-content: space-between; gap: 12px;
    border-top: 1px solid currentColor; border-top-color: rgba(18, 23, 43, 0.18);
    margin-top: 1.25rem; padding-top: 1rem; font-size: 0.85rem;
}
.pg-tone-navy .pg-card-foot { border-top-color: rgba(255, 255, 255, 0.28); }
.pg-price { font-family: var(--pg-display); font-weight: 800; font-size: 2.1rem; letter-spacing: -0.04em; line-height: 1; margin: 0.25rem 0 0.75rem 0; }
.pg-price-strike { text-decoration: line-through; opacity: 0.6; font-size: 1.05rem; font-weight: 600; margin-right: 10px; }
.pg-arrow { flex-shrink: 0; }

/* Inline notice bar */
.pg-note {
    display: flex; align-items: center; gap: 12px; flex-wrap: wrap;
    border: 1px solid var(--pg-line); border-radius: 14px; padding: 0.8rem 1rem; margin: 0 0 1rem 0;
    background: var(--pg-canvas); font-size: 0.9rem; color: var(--pg-body);
}
.pg-note.pg-tone-red { border-color: rgba(168, 50, 43, 0.3); }
.pg-note.pg-tone-sand { border-color: transparent; }
.pg-note.pg-tone-sky { border-color: transparent; }
.pg-codeblock {
    font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; background: rgba(255,255,255,0.6);
    border: 1px dashed rgba(168, 50, 43, 0.45); color: var(--pg-red) !important; border-radius: 10px; padding: 0.6rem 0.8rem; margin-top: 0.5rem;
}

/* Outcome banner */
.pg-banner { border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); padding: 1.75rem 2rem; margin: 0.5rem 0 1.75rem 0; }
.pg-banner h3 { font-size: 1.6rem !important; margin: 0 0 0.75rem 0 !important; padding: 0 !important; line-height: 1.15 !important; }
.pg-banner p { margin: 0 0 0.45rem 0; }
.pg-banner.pg-tone-red h3, .pg-banner.pg-tone-red .pg-eyebrow { color: var(--pg-red) !important; }
.pg-banner.pg-tone-red .pg-dot { background: var(--pg-red); }
.pg-tone-navy .pg-dot { background: #FFFFFF; }

/* ---------- Chips ---------- */
.pg-chip {
    display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;
    padding: 4px 12px; border-radius: 999px; font-size: 0.74rem; font-weight: 600; letter-spacing: 0.02em;
    border: 1px solid var(--pg-line); color: var(--pg-navy) !important; background: var(--pg-surface);
}
.pg-chip-navy { background: var(--pg-navy) !important; border-color: var(--pg-navy); color: #FFFFFF !important; }
.pg-chip-sky { background: var(--pg-sky-soft) !important; border-color: var(--pg-sky); color: var(--pg-navy-deep) !important; }
.pg-chip-sand { background: var(--pg-sand) !important; border-color: #D6CAB0; color: var(--pg-ink) !important; }
.pg-chip-red { background: var(--pg-red-soft) !important; border-color: rgba(168, 50, 43, 0.35); color: var(--pg-red) !important; }
.pg-chip-ghost { background: rgba(255,255,255,0.18) !important; border-color: rgba(255,255,255,0.45); color: #FFFFFF !important; }
.pg-chips { display: flex; flex-wrap: wrap; gap: 8px; }

/* ---------- Numbered steps ---------- */
.pg-steps { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 2.25rem 2.5rem; margin: 0.5rem 0 1.5rem 0; }
.pg-step-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 1.1rem; }
.pg-num {
    width: 46px; height: 46px; border-radius: 50%; border: 1.5px solid var(--pg-sky);
    display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;
    font-size: 0.86rem; font-weight: 600; color: var(--pg-navy); background: var(--pg-surface);
}
.pg-num-red { border-color: rgba(168, 50, 43, 0.5); color: var(--pg-red); }
.pg-num-sand { border-color: #CDBF9F; background: var(--pg-sand-soft); }
.pg-num-navy { background: var(--pg-navy); border-color: var(--pg-navy); color: #FFFFFF; }
.pg-step-title { font-family: var(--pg-display); font-weight: 700; font-size: 1.12rem; letter-spacing: -0.02em; color: var(--pg-ink); margin: 0 0 0.5rem 0; }
.pg-step-text { font-size: 0.9rem; color: var(--pg-muted); line-height: 1.65; margin: 0; }

/* Agent pipeline strip */
.pg-pipeline {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 1px; background: var(--pg-line);
    border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); overflow: hidden; margin: 0.5rem 0 1.5rem 0;
}
.pg-pipe { padding: 1.2rem 1.2rem 1.1rem 1.2rem; background: var(--pg-surface); }
.pg-pipe-idx { font-size: 0.7rem; letter-spacing: 0.18em; font-weight: 600; color: var(--pg-muted); text-transform: uppercase; }
.pg-pipe-name { font-family: var(--pg-display); font-weight: 700; font-size: 1rem; letter-spacing: -0.02em; color: var(--pg-ink); margin: 0.4rem 0 0.75rem 0; }

/* Check list rows */
.pg-checks { margin: 0; padding: 0; list-style: none; }
.pg-checks li { display: flex; gap: 14px; align-items: flex-start; padding: 0.9rem 0; border-bottom: 1px solid var(--pg-line); margin: 0; }
.pg-checks li:last-child { border-bottom: none; }
.pg-check { width: 32px; height: 32px; border-radius: 50%; background: var(--pg-sky); color: var(--pg-navy-deep); display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.pg-check-sand { background: var(--pg-sand); }
.pg-checks .pg-ct { font-weight: 600; color: var(--pg-ink); display: block; margin-bottom: 2px; }
.pg-checks .pg-cd { font-size: 0.9rem; color: var(--pg-muted); }

/* Key/value grid */
.pg-kv { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); border-top: 1px solid var(--pg-line); margin-top: 1.25rem; }
.pg-kv > div { padding: 0.9rem 0; border-bottom: 1px solid var(--pg-line); padding-right: 1rem; }
.pg-kv-label { font-size: 0.68rem; font-weight: 600; letter-spacing: 0.18em; text-transform: uppercase; color: var(--pg-muted); display: block; margin-bottom: 4px; }
.pg-kv-val { font-weight: 600; color: var(--pg-ink); font-size: 0.95rem; }

/* Progress */
.pg-progress { width: 100%; height: 8px; border-radius: 999px; background: var(--pg-sky-soft); overflow: hidden; }
.pg-progress > div { height: 100%; background: var(--pg-navy); border-radius: 999px; }

/* Status dot */
.pg-live { width: 9px; height: 9px; border-radius: 50%; background: var(--pg-navy); display: inline-block; box-shadow: 0 0 0 4px var(--pg-sky-soft); }

/* Comparison table */
.pg-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.pg-table th { text-align: left; font-size: 0.7rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--pg-muted); font-weight: 600; padding: 0.9rem 1rem; border-bottom: 2px solid var(--pg-frame); }
.pg-table td { padding: 1rem; border-bottom: 1px solid var(--pg-line); color: var(--pg-body); vertical-align: top; }
.pg-table td:first-child { font-weight: 600; color: var(--pg-ink); }
.pg-table td.pg-hl, .pg-table th.pg-hl { background: var(--pg-sky-soft); color: var(--pg-navy-deep); }
.pg-mark { display: inline-flex; align-items: center; gap: 8px; }
.pg-mark-no svg { color: var(--pg-red); }
.pg-mark-yes svg { color: var(--pg-navy); }
.pg-table-wrap { border: 2px solid var(--pg-frame); border-radius: var(--pg-radius); overflow-x: auto; background: var(--pg-surface); }

/* ---------- Streamlit widgets ---------- */
/* Buttons: pill shaped */
.stButton > button, .stDownloadButton > button, [data-testid="stPageLink"] a {
    border-radius: 999px !important; font-family: var(--pg-text) !important; font-weight: 600 !important;
    padding: 0.62rem 1.35rem !important; min-height: 2.9rem; transition: background 0.18s ease, color 0.18s ease, border-color 0.18s ease !important;
    box-shadow: none !important;
}
.stButton > button p, .stDownloadButton > button p { font-weight: 600 !important; white-space: pre-line; line-height: 1.3; }
.stButton > button[kind="primary"] {
    background: var(--pg-navy) !important; border: 1.5px solid var(--pg-navy) !important; color: #FFFFFF !important;
}
.stButton > button[kind="primary"] p { color: #FFFFFF !important; }
.stButton > button[kind="primary"] p::after { content: "  \\2197"; font-family: var(--pg-text); }
.stButton > button[kind="primary"]:hover { background: var(--pg-navy-deep) !important; border-color: var(--pg-navy-deep) !important; }
.stButton > button[kind="secondary"], .stDownloadButton > button {
    background: var(--pg-surface) !important; border: 1.5px solid var(--pg-line) !important; color: var(--pg-navy) !important;
}
.stButton > button[kind="secondary"] p, .stDownloadButton > button p { color: var(--pg-navy) !important; }
.stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover {
    border-color: var(--pg-navy) !important; background: var(--pg-sky-soft) !important;
}

[data-testid="stPageLink"] a {
    background: var(--pg-surface) !important; border: 1.5px solid var(--pg-line) !important; justify-content: center;
}
[data-testid="stPageLink"] a:hover { border-color: var(--pg-navy) !important; background: var(--pg-sky-soft) !important; }
[data-testid="stPageLink"] a p, [data-testid="stPageLink"] a span { color: var(--pg-navy) !important; font-weight: 600 !important; }

/* Inputs */
.stTextInput input, .stNumberInput input, .stTextArea textarea,
div[data-baseweb="select"] > div, div[data-baseweb="input"] {
    background: var(--pg-surface) !important; border-color: var(--pg-line) !important; border-radius: 12px !important; color: var(--pg-ink) !important;
}
div[data-baseweb="input"] { border: 1px solid var(--pg-line) !important; }
div[data-baseweb="input"] input { border: none !important; }
.stTextInput input:focus, .stNumberInput input:focus { box-shadow: none !important; }
div[data-baseweb="input"]:focus-within, div[data-baseweb="select"] > div:focus-within { border-color: var(--pg-navy) !important; box-shadow: 0 0 0 3px var(--pg-sky-soft) !important; }
[data-testid="stWidgetLabel"] p, .stRadio > label p, label[data-testid="stWidgetLabel"] p {
    font-size: 0.72rem !important; font-weight: 600 !important; letter-spacing: 0.16em !important; text-transform: uppercase; color: var(--pg-navy) !important;
}
.stNumberInput button { background: var(--pg-canvas) !important; border: none !important; color: var(--pg-navy) !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--pg-canvas) !important; border: 1.5px dashed var(--pg-sky) !important; border-radius: 16px !important; }
[data-testid="stFileUploaderDropzone"] button { border-radius: 999px !important; }

/* Radio as bordered option rows */
.stRadio div[role="radiogroup"] { gap: 0 !important; border: 1px solid var(--pg-line); border-radius: 16px; overflow: hidden; width: 100%; display: flex; flex-direction: column; }
.stRadio div[role="radiogroup"] label { padding: 0.8rem 1rem !important; border-bottom: 1px solid var(--pg-line); margin: 0 !important; width: 100% !important; max-width: none !important; }
.stRadio div[role="radiogroup"] label:last-child { border-bottom: none; }
.stRadio div[role="radiogroup"] label:has(input:checked) { background: var(--pg-sky-soft); }
.stRadio div[role="radiogroup"] label p { text-transform: none !important; letter-spacing: 0 !important; font-size: 0.92rem !important; color: var(--pg-ink) !important; font-weight: 500 !important; }

/* Expanders as FAQ-style rows */
[data-testid="stExpander"] details {
    border: none !important; border-top: 1px solid var(--pg-line) !important; border-bottom: 1px solid var(--pg-line) !important;
    border-radius: 0 !important; background: transparent !important;
}
[data-testid="stExpander"] summary { padding: 1.1rem 0.25rem !important; }
[data-testid="stExpander"] summary p { font-family: var(--pg-text) !important; font-weight: 600 !important; font-size: 1rem !important; color: var(--pg-ink) !important; }
[data-testid="stExpander"] summary svg { color: var(--pg-navy) !important; }
[data-testid="stExpander"] summary:hover p { color: var(--pg-navy) !important; }
[data-testid="stExpanderDetails"] { padding: 0 0.25rem 1.25rem 0.25rem !important; }

/* Tabs as framed segmented tabs (active = navy). Covers both the baseweb
   markup (older Streamlit) and the react-aria markup (newer Streamlit). */
.stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] {
    gap: 0 !important; border: 2px solid var(--pg-frame) !important; border-radius: 18px; overflow: hidden;
    background: var(--pg-surface); display: flex; flex-wrap: nowrap;
}
.stTabs [data-baseweb="tab"], .stTabs [data-testid="stTab"] {
    flex: 1 1 0; min-width: 0 !important; white-space: normal !important; height: auto !important; min-height: 3.6rem; padding: 0.9rem 1.25rem !important;
    display: flex; align-items: center; justify-content: flex-start;
    border-right: 1px solid var(--pg-line) !important; background: var(--pg-surface) !important; margin: 0 !important;
    cursor: pointer;
}
.stTabs [data-baseweb="tab"]:last-child, .stTabs [data-testid="stTab"]:last-child { border-right: none !important; }
.stTabs [data-baseweb="tab"] p, .stTabs [data-testid="stTab"] p {
    font-family: var(--pg-display) !important; font-weight: 700 !important; font-size: 0.98rem !important;
    color: var(--pg-muted) !important; letter-spacing: -0.01em; text-align: left; margin: 0 !important;
}
.stTabs [data-baseweb="tab"]:hover p, .stTabs [data-testid="stTab"]:hover p { color: var(--pg-navy) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"], .stTabs [data-testid="stTab"][aria-selected="true"] { background: var(--pg-navy) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] p, .stTabs [data-testid="stTab"][aria-selected="true"] p { color: #FFFFFF !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"], .stTabs .react-aria-SelectionIndicator { display: none !important; }
.stTabs [data-baseweb="tab-panel"], .stTabs [role="tabpanel"] { padding-top: 1.75rem !important; }
@media (max-width: 760px) {
    .stTabs [data-baseweb="tab-list"], .stTabs [role="tablist"] { flex-wrap: wrap; }
    .stTabs [data-baseweb="tab"], .stTabs [data-testid="stTab"] { flex: 1 1 100%; border-right: none !important; border-bottom: 1px solid var(--pg-line) !important; }
}

/* Alerts */
[data-testid="stAlert"], div[data-testid="stAlertContainer"] {
    border-radius: 16px !important; border: 1px solid var(--pg-line) !important; background: var(--pg-canvas) !important; color: var(--pg-body) !important;
}
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentInfo"] { color: var(--pg-navy-deep) !important; }
[data-testid="stAlertContentWarning"] { color: var(--pg-ink) !important; }
[data-testid="stAlertContentError"] { color: var(--pg-red) !important; }
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]),
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) { background: var(--pg-sky-soft) !important; border-color: var(--pg-sky) !important; }
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { background: var(--pg-sand-soft) !important; border-color: #D6CAB0 !important; }
div[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { background: var(--pg-red-soft) !important; border-color: rgba(168,50,43,0.3) !important; }

/* Captions */
[data-testid="stCaptionContainer"], .stCaption, small { color: var(--pg-muted) !important; }

/* Dataframes */
[data-testid="stDataFrame"], [data-testid="stTable"] { border: 2px solid var(--pg-frame); border-radius: 16px; overflow: hidden; }

/* Images */
[data-testid="stImage"] img { border-radius: 14px; border: 1px solid var(--pg-line); }
</style>
"""


def apply_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def brand_mark() -> None:
    st.markdown(
        '<div class="pg-brand"><div class="pg-brand-word">payguard<span>.</span></div>'
        '<div class="pg-brand-sub">Swarm</div></div>',
        unsafe_allow_html=True,
    )
