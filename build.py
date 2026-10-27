#!/usr/bin/env python3
"""Static site generator for PhotonDispatch (photondispatch.com).

Run:  python3 build.py        (needs Pillow; cairosvg only for the site icons)
Content: content/articles.json   Source images: src-img/   Output: docs/ (GitHub Pages)
See README.md for the daily routine (adding articles, images, 'why it's trending' posts).
"""
import sys, json, os, html, datetime, shutil, re

# ---------------------------------------------------------------- config
SITE_URL = "https://photondispatch.com"  # <-- ONLY place to change the domain
NAME = "PhotonDispatch"; LLC = "Joshua Israel Ventures LLC"; EMAIL = ""  # set a real address here when available; while empty the site shows the GitHub issues link instead
FORM_TO = "4497ee41a1200e746e967998473d21da"  # FormSubmit random alias (activated 23 Oct 2026); used ONLY on contact.html
ISSUES = "https://github.com/joshuaofisrael/photondispatch/issues"; BUILD_DATE = "2026-10-24"
CF_BEACON_TOKEN = os.environ.get("CF_BEACON_TOKEN", "")  # Cloudflare Web Analytics token; "" = disabled
INDEXNOW_KEY = "8cb05bd1e79a50594f6726934d66a801"
DESC = "Independent, answer-first quantum computing and quantum technology news: hardware, algorithms, industry and funding, research and policy."
OUT = "docs"; ASSET_VER = "4"
# ----------------------------------------------------------------

TODO_IMAGES = []
CATS = [("hardware","Hardware"),("algorithms","Algorithms"),("industry","Industry & Funding"),("research","Research"),("policy","Policy")]
CATN = dict(CATS)
A = json.load(open("content/articles.json", encoding="utf-8"))
# Legal-hold gate: held articles are never rendered (approved exact versions pass).
sys.path.insert(0, "review"); import check_content as _cc
_ok = _cc.approvals(); _keep = []
for _a in A:
    _f = _cc.check(_a)
    if _f and (_a.get("slug"), _cc.version_hash(_a)) not in _ok:
        print(f"  [HOLD_REVIEW] {_a.get('slug')} not built: rules {sorted({x[0] for x in _f})}"); _cc.queue(_a, _f, "content/articles.json")
    else: _keep.append(_a)
A = _keep
A.sort(key=lambda a: a["date"], reverse=True)
PUB = {"@type": "Organization", "name": "PhotonDispatch", "url": SITE_URL + "/", "parentOrganization": {"@type": "Organization", "name": "Joshua Israel Ventures LLC"}, "logo": {"@type": "ImageObject", "url": SITE_URL + "/logo.png", "width": 512, "height": 512}}

def esc(s): return html.escape(s, quote=True)
def fd(d): return datetime.date.fromisoformat(d).strftime("%-d %B %Y")

MARK = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" aria-hidden="true"><rect width="64" height="64" rx="14" fill="#0a0e14"/><rect x="1.5" y="1.5" width="61" height="61" rx="12.5" fill="none" stroke="#22d3ee" stroke-opacity=".35"/><path d="M20 22a6 6 0 0 1 6-6h12a6 6 0 0 1 6 6v14a6 6 0 0 1-6 6H26a6 6 0 0 1-6-6z" fill="none" stroke="#22d3ee" stroke-width="3"/><rect x="24" y="25" width="16" height="6" rx="3" fill="#a3e635"/><path d="M32 16v-5M26 42v6h12v-6M14 30h6M44 30h6" stroke="#22d3ee" stroke-width="3" stroke-linecap="round"/><circle cx="32" cy="10" r="2.5" fill="#22d3ee"/></svg>'

HERO_SVG = '''<svg class="hero-fx" viewBox="0 0 1200 520" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
<g fill="none" stroke="#22d3ee" stroke-opacity=".55" stroke-width="2" class="flow"><path d="M560 60h180l40 40h160"/><path d="M1200 140h-160l-40 40h-90"/><path d="M620 470h160l50-50h140"/><path d="M1200 400h-120l-40-40h-80"/></g>
<g fill="#22d3ee"><circle class="pulse" cx="740" cy="60" r="5"/><circle class="pulse" cx="1000" cy="180" r="5" style="animation-delay:.6s"/><circle class="pulse" cx="780" cy="470" r="5" style="animation-delay:1.2s"/><circle class="pulse" cx="1040" cy="360" r="5" style="animation-delay:1.8s"/></g></svg>'''

# ---------------------------------------------------------------- images
IMG_DIRS_READY = False
def make_images(name, spec):
    """Create docs/img/<name>.jpg (1200x630, og), <name>-1200.webp, <name>-600.webp from a photo spec or generated art."""
    from PIL import Image
    os.makedirs(OUT + "/img", exist_ok=True)
    if True:
        im = Image.open(spec["src"]).convert("RGB"); W, H = im.size
        l, t, w = spec.get("crop", [0, 0, 1.0])
        cw = int(W * w); ch = int(cw * 630 / 1200); x = int(W * l); y = int(H * t)
        im = im.crop((x, y, x + cw, min(y + ch, H))).resize((1200, 630), Image.LANCZOS)
    im.save(f"{OUT}/img/{name}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
    im.save(f"{OUT}/img/{name}-1200.webp", "WEBP", quality=76, method=6)
    im.resize((600, 315), Image.LANCZOS).save(f"{OUT}/img/{name}-600.webp", "WEBP", quality=74, method=6)

def img_tag(name, alt, eager=False, sizes="(max-width:760px) 100vw, 520px", r=""):
    ld = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<img src="{r}img/{name}-1200.webp" srcset="{r}img/{name}-600.webp 600w, {r}img/{name}-1200.webp 1200w" sizes="{sizes}" '
            f'width="1200" height="630" alt="{esc(alt)}" {ld} decoding="async">')


# ---------------------------------------------------------------- inline images
ASSETS_DIR = "/workspace/photon-assets"
def make_inline(slug, n, spec):
    """Convert one inline_images entry. Returns dict(w,h,name) or None when the source file has not been supplied yet."""
    import shutil
    from PIL import Image
    f = spec["file"]
    p = f if os.path.isabs(f) else os.path.join(ASSETS_DIR, f)
    keep = os.path.join("src-img", "inline", os.path.basename(f))
    if os.path.exists(p):
        os.makedirs("src-img/inline", exist_ok=True)
        if os.path.abspath(p) != os.path.abspath(keep): shutil.copyfile(p, keep)
    elif os.path.exists(keep): p = keep
    else:
        print(f"  [inline pending] {slug}-{n}: {f} not found"); return None
    im = Image.open(p).convert("RGB"); W, H = im.size
    name = f"{slug}-{n}"; w = 1200; h = round(H * w / W)
    os.makedirs(OUT + "/img", exist_ok=True)
    im.resize((w, h), Image.LANCZOS).save(f"{OUT}/img/{name}-1200.webp", "WEBP", quality=76, method=6)
    im.resize((600, round(H * 600 / W)), Image.LANCZOS).save(f"{OUT}/img/{name}-600.webp", "WEBP", quality=74, method=6)
    return {"name": name, "w": w, "h": h, "w6": 600, "h6": round(H * 600 / W), "src": p, "srcw": W}

def inline_fig(m, spec):
    cap = (esc(spec["caption"]).rstrip(". ") + ". " if spec.get("caption") else "") + "AI-generated image"
    return (f'<figure class="inl"><img src="../img/{m["name"]}-1200.webp" srcset="../img/{m["name"]}-600.webp 600w, ../img/{m["name"]}-1200.webp 1200w" '
            f'sizes="(max-width:760px) 100vw, 720px" width="{m["w"]}" height="{m["h"]}" alt="{esc(spec["alt"])}" loading="lazy" decoding="async">'
            f'<figcaption>{cap}</figcaption></figure>')

def is_ai(im): return bool(im.get("ai"))
AI_LICENCE = "generated; rights held by the site owner (see terms.html)"
def credit_html(im):
    if is_ai(im): return "AI-generated image"
    s = f'Photo: {esc(im["credit"])}'
    if im.get("source_url"): s += f' · <a href="{esc(im["source_url"])}" rel="noopener">Source</a>'
    return s + f' · {esc(im["license"])}'

# ---------------------------------------------------------------- page shell
def page(path, title, desc, content, depth=0, ld=None, typ="website", image=None, base=None, extra_head=""):
    r = base if base is not None else "../" * depth
    url = SITE_URL + "/" + path.replace("index.html", "")
    catnav = "".join(f'<a href="{r}category/{c}.html">{t}</a>' for c, t in CATS)
    og = image or {"url": f"{SITE_URL}/img/og-default.jpg", "alt": NAME + ": quantum technology news"}
    lds = [{"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE_URL + "/", "publisher": PUB}] + ([ld] if ld else [])
    beacon = f'<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon=\'{{"token": "{CF_BEACON_TOKEN}"}}\'></script>' if CF_BEACON_TOKEN else ""
    robots = "noindex" if path == "404.html" else "index,follow,max-image-preview:large,max-snippet:-1"
    h = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(desc)}"><link rel="canonical" href="{url}">
<meta name="robots" content="{robots}"><meta name="theme-color" content="#0a0e14">
<meta property="og:type" content="{typ}"><meta property="og:site_name" content="{NAME}"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:url" content="{url}">
<meta property="og:image" content="{og['url']}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="{esc(og['alt'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(desc)}"><meta name="twitter:image" content="{og['url']}"><meta name="twitter:image:alt" content="{esc(og['alt'])}">
{extra_head}<link rel="icon" href="{r}favicon.svg" type="image/svg+xml"><link rel="icon" href="{r}favicon-32.png" sizes="32x32" type="image/png"><link rel="apple-touch-icon" href="{r}apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="{NAME}" href="{r}feed.xml"><link rel="stylesheet" href="{r}assets/style.css?v={ASSET_VER}">
""" + "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds) + f"""</head><body>
<a class="skip" href="#main">Skip to content</a><div class="progress" aria-hidden="true"></div>
<header class="site-h"><div class="w"><a class="logo" href="{r}index.html" aria-label="{NAME} home">{MARK}<span>Photon<b>Dispatch</b></span></a><nav aria-label="Main"><a href="{r}index.html">News</a>{catnav}<a href="{r}about.html">About</a><a href="{r}contact.html">Contact</a><a href="{r}feed.xml">RSS</a></nav></div></header>
<main id="main">{content}</main>
<footer class="site-f"><div class="w"><p><a href="{r}about.html">About</a> · <a href="{r}standards.html">Editorial standards</a> · <a href="{r}corrections.html">Corrections</a> · <a href="{r}contact.html">Contact</a> · <a href="{r}terms.html">Terms</a> · <a href="{r}privacy.html">Privacy</a> · <a href="{r}disclaimer.html">Disclaimer</a> · <a href="{r}copyright.html">Copyright</a> · <a href="{r}disclosure.html">Ad &amp; affiliate disclosure</a> · <a href="{r}feed.xml">RSS</a></p>
</div></footer>
<script defer src="{r}assets/app.js?v={ASSET_VER}"></script>{beacon}</body></html>"""
    p = os.path.join(OUT, path); os.makedirs(os.path.dirname(p) or OUT, exist_ok=True); open(p, "w", encoding="utf-8").write(h)

# ---------------------------------------------------------------- build
shutil.rmtree(OUT + "/img", ignore_errors=True); os.makedirs(OUT + "/news", exist_ok=True); os.makedirs(OUT + "/assets", exist_ok=True)
for f in ("style.css", "app.js"): shutil.copy("assets/" + f, f"{OUT}/assets/{f}")

# site-level images
open(OUT + "/favicon.svg", "w").write(MARK.replace(' aria-hidden="true"', ""))
try:
    import cairosvg
    cairosvg.svg2png(bytestring=MARK.encode(), write_to=OUT + "/favicon-32.png", output_width=32, output_height=32)
    cairosvg.svg2png(bytestring=MARK.encode(), write_to=OUT + "/apple-touch-icon.png", output_width=180, output_height=180)
    cairosvg.svg2png(bytestring=MARK.encode(), write_to=OUT + "/logo.png", output_width=512, output_height=512)
except ImportError:
    print("WARN: cairosvg missing; kept existing icon PNGs")
HERO_SPEC = {"src": "src-img/photon-hero.jpg", "crop": [0, 0.05, 1.0], "ai": True, "alt": "Gold-plated cryogenic quantum computer chandelier in a dim violet-lit lab"}
make_images("og-default", HERO_SPEC)
from PIL import Image as _I
_h = _I.open(HERO_SPEC["src"]).convert("RGB")
_h.resize((1920, 1080), _I.LANCZOS).save(OUT + "/img/hero-1920.webp", "WEBP", quality=70, method=6)
_h.resize((1200, 675), _I.LANCZOS).save(OUT + "/img/hero-1200.webp", "WEBP", quality=74, method=6)
_h.save(OUT + "/img/hero.jpg", "JPEG", quality=76, optimize=True, progressive=True)
if os.path.exists(OUT + "/og.svg"): os.remove(OUT + "/og.svg")

def has_img(a): return bool(a.get("image"))
for a in A:
    if has_img(a): make_images(a["slug"], a["image"])
    a["_og"] = {"url": f"{SITE_URL}/img/{a['slug']}.jpg", "alt": a["image"]["alt"]} if has_img(a) else None

def card(a, feat=False, eager=False):
    im = ""
    if has_img(a):
        sizes = "(max-width:760px) 100vw, 620px" if feat else "(max-width:760px) 100vw, 520px"
        im = f'<div class="im">{img_tag(a["slug"], a["image"]["alt"], eager, sizes)}</div>'
    tag = '<span class="tag trend">Trending</span> ' if a.get("kind") == "trending" else ""
    return (f'<article class="card reveal{" feat" if feat else ""}">{im}<div class="tx">{tag}<a class="tag" href="category/{a["cat"]}.html">{esc(CATN[a["cat"]])}</a>'
            f'<h3><a href="news/{a["slug"]}.html">{esc(a["title"])}</a></h3><p class="meta"><time datetime="{a["date"]}">{fd(a["date"])}</time></p><p>{esc(a["summary"])}</p></div></article>')

trend = [a for a in A if a.get("kind") == "trending"][:4]
rest = [a for a in A if a not in trend]
sections = ""
if trend: sections += '<section class="sec"><div class="w"><h2 class="sh">Why it\'s trending</h2><div class="grid">' + "".join(card(a) for a in trend) + '</div></div></section>'
sections += '<section class="sec" id="latest"><div class="w"><h2 class="sh">Latest news</h2><div class="grid">' + "".join(card(a, feat=(i == 0), eager=(i == 0)) for i, a in enumerate(rest)) + '</div></div></section>'
cos = ["IBM", "Google Quantum AI", "Quantinuum", "IonQ", "Rigetti", "D-Wave", "PsiQuantum", "Pasqal", "IQM", "Microsoft", "NVIDIA CUDA-Q", "Post-quantum cryptography"]
sections += '<section class="sec"><div class="w"><h2 class="sh">What we cover</h2><ul class="chips">' + "".join(f"<li>{c}</li>" for c in cos) + "</ul></div></section>"
hero = (f'<section class="hero hero-photo"><picture><source type="image/webp" srcset="img/hero-1200.webp 1200w, img/hero-1920.webp 1920w" sizes="100vw">'
        f'<img class="hero-bg" src="img/hero.jpg" width="1920" height="1080" alt="Gold-plated cryogenic quantum computer chandelier in a dim violet-lit lab (AI-generated image)" fetchpriority="high" decoding="async"></picture>'
        f'<div class="hero-shade"></div>{HERO_SVG}<div class="w"><div class="hero-tx"><span class="kicker">Quantum technology · daily</span><h1>Quantum news, <em>answered first.</em></h1><p>{esc(DESC)}</p><a class="btn" href="#latest">Read the latest</a><a class="btn ghost" href="feed.xml">RSS feed</a><p class="cap">AI-generated image</p></div></div></section>')
page("index.html", f"{NAME}: Quantum Computing & Quantum Tech News", DESC, hero + sections, 0, extra_head='<link rel="preload" as="image" type="image/webp" href="img/hero-1200.webp" imagesrcset="img/hero-1200.webp 1200w, img/hero-1920.webp 1920w" imagesizes="100vw" fetchpriority="high">')

for a in A:
    u = f"{SITE_URL}/news/{a['slug']}.html"
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": a["title"], "description": a["summary"], "datePublished": a["date"], "dateModified": a.get("updated", a["date"]),
          "mainEntityOfPage": u, "isAccessibleForFree": True, "inLanguage": "en", "author": {"@type": "Organization", "name": NAME + " Staff"}, "publisher": PUB, "isBasedOn": [s["url"] for s in a["sources"]]}
    ld["image"] = [{"@type": "ImageObject", "url": a["_og"]["url"], "width": 1200, "height": 630}] if a["_og"] else [SITE_URL + "/img/og-default.jpg"]
    fig = ""
    # (inline images are added to JSON-LD after they are built, below)
    if has_img(a):
        fig = f'<div class="a-hero"><figure>{img_tag(a["slug"], a["image"]["alt"], True, "(max-width:980px) 100vw, 980px", "../")}<figcaption>{credit_html(a["image"])}</figcaption></figure></div>'
    ins = {}
    a["_inl"] = []
    for n, sp in enumerate(a.get("inline_images", []), 1):
        m = make_inline(a["slug"], n, sp)
        if m: ins.setdefault(int(sp["insert_after_paragraph"]), []).append(inline_fig(m, sp)); a["_inl"].append((m, sp))
    body = "".join(f'<p{" class=lede" if i == 0 else ""}>{p}</p>' + "".join(ins.get(i + 1, [])) for i, p in enumerate(a["body"]))
    if isinstance(ld.get("image"), list):
        ld["image"] += [{"@type": "ImageObject", "url": f"{SITE_URL}/img/{m['name']}-1200.webp", "width": m["w"], "height": m["h"], "caption": sp.get("caption") or sp["alt"]} for m, sp in a["_inl"]]
    upd = a.get("updated", a["date"])
    ana = "".join(f'<aside class="note analysis"><h2>Analysis</h2><p>{p}</p></aside>' for p in a.get("analysis", []))
    dis = f'<aside class="note"><strong>Note:</strong> {a["disclaimer"]}</aside>' if a.get("disclaimer") else ""
    why = ""
    if a.get("kind") == "trending" and a.get("why"):
        why = '<aside class="why"><h2>Why it\'s trending</h2><ul>' + "".join(f"<li>{w}</li>" for w in a["why"]) + "</ul></aside>"
    src = "".join(f'<li><a href="{esc(s["url"])}" rel="noopener">{esc(s["title"])}</a></li>' for s in a["sources"])
    tag = '<span class="tag trend">Trending</span> ' if a.get("kind") == "trending" else ""
    c = f'{fig}<article class="prose art"><p style="margin:24px 0 0">{tag}<a class="tag" href="../category/{a["cat"]}.html">{esc(CATN[a["cat"]])}</a></p><h1>{esc(a["title"])}</h1><p class="meta" style="font-size:.9rem">By {NAME} Staff · Published <time datetime="{a["date"]}">{fd(a["date"])}</time> · Last updated <time datetime="{upd}">{fd(upd)}</time></p>{body}{ana}{why}{dis}<div class="src"><h2>Sources</h2><p class="meta">Every factual claim above comes from these sources. See our <a href="../standards.html">editorial standards</a> and <a href="../corrections.html">corrections policy</a>.</p><ul>{src}</ul></div><p><a href="../index.html">← All news</a></p></article>'
    page(f"news/{a['slug']}.html", f"{a['title']} | {NAME}", a["summary"], c, 1, ld, "article", a["_og"])

for c, t in CATS:
    items = [a for a in A if a["cat"] == c]
    g = "".join(card(a).replace('href="news/', 'href="../news/').replace('href="category/', 'href="../category/').replace('src="img/', 'src="../img/').replace('img/', '../img/').replace('../../img/', '../img/') for a in items) or "<p>No stories in this section yet.</p>"
    page(f"category/{c}.html", f"{t} | Quantum News | {NAME}", f"Latest quantum {t.lower()} news from {NAME}.", f'<section class="sec"><div class="w"><h1 class="sh">{t}</h1><div class="grid">{g}</div></div></section>', 1)
L = f"<strong>{LLC}</strong>"
CORRECTIONS = []
CLOG = "<p>No corrections yet.</p>" if not CORRECTIONS else "<ul>" + "".join(f'<li><time datetime="{d}">{fd(d)}</time> · <a href="news/{sl}.html">{sl.replace("-", " ")}</a>: {esc(t)}</li>' for d, sl, t in CORRECTIONS) + "</ul>"
CONTACT = (f'<p>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>' if EMAIL else '') + f'<p>Open an issue on our public tracker: <a href="{ISSUES}" rel="noopener">{ISSUES}</a></p>'
analytics = "We use Cloudflare Web Analytics, a privacy-focused service that measures page views without cookies or cross-site tracking. " if CF_BEACON_TOKEN else ""
FORM = f'''<h2>Send us a message</h2><div id="thanks" class="note" role="status" tabindex="-1" hidden><h2>Thank you</h2><p>Your message has been sent. We will reply if a response is needed.</p></div><form id="cf" class="cf" method="POST" action="https://formsubmit.co/{FORM_TO}" data-ajax="https://formsubmit.co/ajax/{FORM_TO}"><p><label for="cf-name">Name</label><input id="cf-name" name="name" type="text" autocomplete="name" required maxlength="120"></p><p><label for="cf-email">Email</label><input id="cf-email" name="email" type="email" autocomplete="email" required maxlength="200"></p><p><label for="cf-msg">Message</label><textarea id="cf-msg" name="message" rows="6" required maxlength="4000"></textarea></p><input type="text" name="_honeypot" tabindex="-1" autocomplete="off" aria-hidden="true" style="position:absolute;left:-9999px;width:1px;height:1px;opacity:0"><input type="hidden" name="_subject" value="PhotonDispatch contact"><input type="hidden" name="_captcha" value="false"><input type="hidden" name="_template" value="table"><input type="hidden" name="_next" value="{SITE_URL}/contact.html?sent=1#thanks"><p><button type="submit" class="btn">Send message</button></p><p id="cf-err" role="alert" hidden>Sorry, the message could not be sent. Please try again, or use the GitHub link below.</p><p class="fine">Messages are emailed to the site owner only so we can respond. They are not shared or sold. See our <a href="privacy.html">privacy policy</a>.</p></form>'''
legal = {
"about.html": ("About", f"<h1>About {NAME}</h1><p>{NAME} is an independent publication covering quantum computing and quantum technology: hardware, algorithms, industry and funding, research and policy. Our brand line: <strong>quantum news, answered first.</strong> Every story is written originally, leads with the answer, and links to the sources its facts come from. We do not invent facts or quotes. See our <a href=\"standards.html\">editorial standards</a>, <a href=\"corrections.html\">corrections policy</a> and <a href=\"contact.html\">contact page</a>.</p><h2>Images</h2><p>All images on {NAME} are AI-generated, photorealistic scenes created for illustration and captioned \"AI-generated image\". They are generic and do not depict real people or real news events. Details are in the site repository (<code>images.md</code>).</p>"),
"contact.html": ("Contact", f"<h1>Contact</h1>{FORM}<h2>Alternative: public issue tracker</h2>{CONTACT}<p>For corrections, please include the article link, the sentence in question, and a source that supports the fix. Please do not post private personal information in a public issue. See our <a href=\"corrections.html\">corrections policy</a>.</p>"),
"corrections.html": ("Corrections Policy", f"<h1>Corrections Policy</h1><p>We aim to be accurate. If we get something wrong, we fix it and say so.</p><h2>How we correct</h2><ul><li>Factual errors are corrected in the article as soon as they are verified, and the article's <strong>Last updated</strong> date changes.</li><li>Significant corrections are logged below with the date and what changed.</li><li>If a claim cannot be verified against a cited source, we soften it or remove it.</li><li>We will review and, where justified, remove or amend content about a named person or company on request, once the concern is identified and the sources checked.</li></ul><h2>How to report an error</h2>{CONTACT}<h2>Corrections log</h2>{CLOG}"),
"standards.html": ("Editorial Standards", f"<h1>Editorial Standards: Sources and Ethics</h1><h2>Sourcing</h2><ul><li>Every factual claim must trace to a named, linkable source (company announcement, regulator or government release, filing, or reputable news outlet) listed at the bottom of the article.</li><li>We prefer primary sources and say when a claim is only a company's own statement (\"according to the company\").</li><li>We do not publish unsourced numbers, dates, or quotes. If we cannot verify something, we leave it out.</li></ul><h2>Original writing</h2><ul><li>Articles are written in our own words. We use only brief, attributed quotations.</li></ul><h2>Fairness</h2><ul><li>We do not state or imply wrongdoing by any person or company unless an authoritative source reports it, and then we attribute it.</li><li>We do not speculate about individuals.</li></ul><h2>Opinion and analysis</h2><ul><li>Analysis and opinion are clearly labelled as such and kept separate from reported facts.</li></ul><h2>Company announcements vs. verified claims</h2><ul><li>Statements, figures and timelines that come from a company's own announcement are attributed to that company, and we say when they have not been independently verified.</li><li>We describe something as confirmed only where an independent source we cite supports it.</li><li>Targets, forecasts and roadmaps stated by companies are reported as their targets, not as outcomes. We do not promise or imply any result for readers, customers or investors.</li></ul><h2>Images</h2><ul><li>Images are AI-generated photorealistic scenes, captioned \"AI-generated image\". They do not depict real identifiable people or real news events.</li></ul><h2>Not advice</h2><ul><li>Nothing on the site is investment, legal, medical or other professional advice. Articles about funding or listed companies are reports of announcements, not recommendations.</li></ul><h2>Updates</h2><ul><li>Each article shows its published and last-updated dates. See the <a href=\"corrections.html\">corrections policy</a>.</li></ul><p>Independence: {NAME} is not affiliated with the companies it covers unless stated. Ownership details are in our <a href=\"terms.html\">Terms of Use</a>.</p><p><em>Last updated: 24 October 2026.</em></p>"),
"terms.html": ("Terms of Use", f"<h1>Terms of Use</h1><p>These Terms govern your use of {NAME}, owned and operated by {L} (\"we\"). By using the site you agree to them.</p><h2>Content</h2><p>All original content is © 2026 {LLC}. You may share links and brief quotations with attribution. Third-party trademarks belong to their owners and are used for identification only.</p><h2>No warranty</h2><p>The site is provided \"as is\" without warranties of any kind. To the fullest extent permitted by law, {LLC} is not liable for any damages arising from your use of the site.</p><h2>Governing law</h2><p>These Terms are governed by the laws of the State of Florida, USA, and any dispute shall be resolved in the state or federal courts located in Florida.</p><h2>Changes</h2><p>We may update these Terms; continued use means acceptance.</p>"),
"privacy.html": ("Privacy Policy", f"<h1>Privacy Policy</h1><p>This policy explains how {L}, operator of {NAME}, handles information.</p><h2>What we collect</h2><p>{analytics}Our hosting provider (GitHub Pages) may log standard technical data (such as IP address and browser type) for security and operations. If you contact us through the contact form, your name, email address and message are sent by email to the site owner via the FormSubmit.co form service, and we keep them only to respond.</p><h2>Cookies and advertising</h2><p>This site does not currently use advertising, analytics or tracking cookies. If we add advertising or analytics in future, we will update this policy and, where required (for example for visitors in the EU and UK), ask for consent first.</p><h2>Sharing</h2><p>We do not sell personal information.</p><h2>Your rights</h2><p>You may request access to or deletion of information you sent us through our <a href=\"contact.html\">contact page</a>.</p><h2>Governing law</h2><p>This policy is governed by the laws of the State of Florida, USA.</p>"),
"disclaimer.html": ("Disclaimer", f"<h1>Disclaimer</h1><p>Content on {NAME} is for general information only and is not investment, legal or professional advice. We work to verify facts against cited sources but cannot guarantee completeness, accuracy or timeliness, and we accept no liability for any loss or damage arising from reliance on the content, to the fullest extent permitted by law. Reports of funding, earnings or company plans are summaries of announcements, not recommendations to buy, sell or hold any security. Images are AI-generated illustrations and not photographs of real events. {NAME} is not affiliated with any company it covers unless stated. Company names, product names and logos are trademarks of their owners. {NAME} is owned and operated by {L}, and this disclaimer is governed by the laws of the State of Florida, USA.</p>"),
"copyright.html": ("Copyright and DMCA Policy", f"<h1>Copyright and DMCA Policy</h1><p>All original articles, text and AI-generated images on {NAME} are owned by {L} unless otherwise noted. You may link to our articles and quote brief excerpts with attribution and a link back. Republishing full articles or images requires written permission.</p><h2>Reporting infringement (DMCA)</h2><p>If you believe material on {NAME} infringes your copyright, send a notice through our <a href=\"contact.html\">contact form</a> that includes: (1) your physical or electronic signature; (2) identification of the copyrighted work; (3) the URL of the material you claim is infringing; (4) your contact information; (5) a statement that you have a good-faith belief the use is not authorized by the copyright owner, its agent or the law; and (6) a statement, under penalty of perjury, that the information is accurate and that you are the owner or authorized to act on the owner's behalf. We will review valid notices promptly and remove or disable access to infringing material where appropriate.</p><h2>Counter-notice</h2><p>If your material was removed and you believe this was a mistake, you may send a counter-notice through the same form with the details required by 17 U.S.C. § 512(g).</p><h2>Trademarks</h2><p>Company and product names mentioned on the site are trademarks of their respective owners and are used for identification only.</p><h2>Governing law</h2><p>This policy is governed by the laws of the State of Florida, USA.</p>"),
"disclosure.html": ("Advertising and Affiliate Disclosure", f"<h1>Advertising and Affiliate Disclosure</h1><p>{NAME} is owned and operated by {L}. We currently do not display advertising and do not participate in affiliate programs. No company pays us to cover it, and coverage is never for sale.</p><p>If we add advertising, sponsored content or affiliate links in future, they will be clearly labelled, this page will be updated, and our editorial decisions will remain independent of any commercial relationship. Where we receive compensation, such as a commission when you buy through a link, we will say so near the link, in line with the U.S. Federal Trade Commission's Endorsement Guides.</p><h2>Governing law</h2><p>This disclosure is governed by the laws of the State of Florida, USA.</p>"),
}
CR = "<p>© 2026 Joshua Israel Ventures LLC. All rights reserved. PhotonDispatch is a trade name of Joshua Israel Ventures LLC, a Florida limited liability company.</p>"
LEGAL = ("terms.html", "privacy.html", "disclaimer.html", "copyright.html", "disclosure.html")
for f in LEGAL: legal[f] = (legal[f][0], legal[f][1] + CR)
for f, (t, c) in legal.items(): page(f, f"{t} | {NAME}", (f"{t} for {NAME}, operated by {LLC}." if f in LEGAL else f"{t} for {NAME}."), f'<div class="prose page">{c}</div>', 0)
page("404.html", f"Page not found | {NAME}", "Page not found.", f'<div class="prose page"><h1>Page not found</h1><p>That page does not exist. <a href="{SITE_URL}/index.html">Go to the latest news</a>.</p></div>', 0, base=SITE_URL + "/")

# sitemap (with image extension), robots, llms, feed, indexnow key
urls = [("", max(a.get("updated", a["date"]) for a in A), None)] + [(f"news/{a['slug']}.html", a.get("updated", a["date"]), a["_og"]) for a in A] + [(f"category/{c}.html", BUILD_DATE, None) for c, _ in CATS] + [(f, BUILD_DATE, None) for f in legal]
def sm(u, d, im):
    x = f"<url><loc>{SITE_URL}/{u}</loc><lastmod>{d}</lastmod>"
    if im: x += f"<image:image><image:loc>{im['url']}</image:loc></image:image>"
    return x + "</url>"
open(OUT + "/sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">' + "".join(sm(*x) for x in urls) + "</urlset>\n")
bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-Web", "anthropic-ai", "PerplexityBot", "CCBot", "Google-Extended", "Applebot", "Applebot-Extended", "Bytespider", "Amazonbot", "Meta-ExternalAgent"]
open(OUT + "/robots.txt", "w").write("".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n")
open(OUT + f"/{INDEXNOW_KEY}.txt", "w").write(INDEXNOW_KEY)
open(OUT + "/llms.txt", "w").write(f"# {NAME}\n\n> {DESC}\n\n## Articles\n" + "".join(f"- [{a['title']}]({SITE_URL}/news/{a['slug']}.html): {a['summary']}\n" for a in A) + f"\n## About\n- [About]({SITE_URL}/about.html)\n- [Editorial standards]({SITE_URL}/standards.html)\n- [Corrections]({SITE_URL}/corrections.html)\n- [Contact]({SITE_URL}/contact.html)\n- [RSS]({SITE_URL}/feed.xml)\n")
def rfc(d): return datetime.datetime.fromisoformat(d + "T12:00:00+00:00").strftime("%a, %d %b %Y %H:%M:%S +0000")
open(OUT + "/feed.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:media="http://search.yahoo.com/mrss/"><channel><title>{NAME}</title><link>{SITE_URL}/</link><description>{esc(DESC)}</description><language>en</language><atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>' + "".join(f"<item><title>{esc(a['title'])}</title><link>{SITE_URL}/news/{a['slug']}.html</link><guid>{SITE_URL}/news/{a['slug']}.html</guid><pubDate>{rfc(a['date'])}</pubDate><description>{esc(a['summary'])}</description>" + (f'<media:content url="{a["_og"]["url"]}" type="image/jpeg" medium="image" width="1200" height="630"/>' if a["_og"] else "") + "</item>" for a in A) + "</channel></rss>\n")
open(OUT + "/.nojekyll", "w").write("")
if os.path.exists("docs/CNAME") is False and SITE_URL.startswith("https://") and "github.io" not in SITE_URL:
    open("docs/CNAME", "w").write(SITE_URL.split("//")[1] + "\n")

# images.md: source + licence per image
L2 = ["# Image credits and licences", "", "Generated by `build.py` from `content/articles.json`. Do not edit by hand; add a `note` in the article's `image` object instead.", "",
      "House rule: imagery is AI-generated hyper-realistic photography (supplied as files via /workspace) with the caption 'AI-generated image'.", "",
      "| Image | Used in | Type | Credit | Licence | Source | Note |", "|---|---|---|---|---|---|---|",
      f"| hero.jpg, hero-1200/1920.webp, og-default.jpg | Homepage hero + default og:image | AI-generated photo | AI-generated image | {AI_LICENCE} | src-img/photon-hero.jpg | 1024x576 source; 1920 variant is upscaled |",
      f"| favicon, logo, icons | Site-wide | Generated | PhotonDispatch original artwork | {AI_LICENCE} | n/a | |"]
for a in A:
    if not has_img(a): continue
    im = a["image"]
    if is_ai(im): L2.append(f"| {a['slug']}.jpg | {a['slug']} | {'AI-generated photo' if 'src' in im else 'Generated illustration'} | AI-generated image | {AI_LICENCE} | {im.get('src','n/a')} | {im.get('note','')} |")
    else: L2.append(f"| {a['slug']}.jpg | {a['slug']} | {im.get('kind','photo')} | {im['credit']} | {im['license']} | {im.get('source_url','')} | {im.get('note','')} |")
for a in A:
    for m, sp in a["_inl"]:
        L2.append(f"| {m['name']}-600/1200.webp | {a['slug']} (inline, after paragraph {sp['insert_after_paragraph']}) | AI-generated photo | AI-generated image | {AI_LICENCE} | {os.path.basename(sp['file'])} | {m['srcw']}px-wide source; {sp.get('note','')} |")
pending = [f"Generate `{sp['file']}` in /workspace/photon-assets/ for `{a['slug']}` (inline image {n}, after paragraph {sp['insert_after_paragraph']}): {sp.get('brief', sp['alt'])}"
           for a in A for n, sp in enumerate(a.get("inline_images", []), 1) if sp not in [x[1] for x in a["_inl"]]]
L2 += ["", "## TODO (images)", ""] + [f"- [ ] {t}" for t in pending + TODO_IMAGES]
open("images.md", "w").write("\n".join(L2) + "\n")
print("built", len(A), "articles")
