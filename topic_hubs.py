"""Topic hubs for PhotonDispatch (added 12 Nov 2026).
Each hub collects every published article whose title or summary matches the topic, newest first,
so readers and crawlers can follow one company or technology across stories. Rebuilt on every build.py run."""
import re
TOPICS = [
 ("ibm", "IBM", r"\bibm\b", "Every PhotonDispatch story about IBM's quantum computing work: processors, roadmaps, partnerships and research, each linked to its sources."),
 ("ionq", "IonQ", r"\bionq\b", "Every PhotonDispatch story about IonQ: trapped ion systems, deals, acquisitions and company announcements, each linked to its sources."),
 ("quantinuum", "Quantinuum", r"quantinuum", "Every PhotonDispatch story about Quantinuum: trapped ion hardware, error correction results and company news, each linked to its sources."),
 ("google-quantum-ai", "Google Quantum AI", r"\bgoogle\b", "Every PhotonDispatch story about Google's quantum computing work, including Google Quantum AI research and hardware, each linked to its sources."),
 ("error-correction", "Quantum error correction", r"error.correct|logical qubit|decod", "Stories on quantum error correction: logical qubits, decoders and fault tolerance results, each linked to its sources. Company claims are attributed as such."),
 ("trapped-ions", "Trapped ion quantum computing", r"trapped.ion|\bionq\b|quantinuum", "Stories on trapped ion quantum computers, which use individual charged atoms held in electromagnetic traps as qubits, each linked to its sources."),
 ("photonic", "Photonic quantum computing", r"photonic|psiquantum", "Stories on photonic quantum computing, which uses particles of light as qubits, each linked to its sources."),
]
def matches(a, rx): return re.search(rx, (a["title"] + " " + a["summary"]).lower()) is not None
def topics_for(a): return [(s, n) for s, n, rx, _ in TOPICS if matches(a, rx)]
def build(A, page, card, esc, SITE_URL):
    out = []
    fix = lambda h: h.replace('href="news/', 'href="../news/').replace('href="category/', 'href="../category/').replace('img/', '../img/').replace('../../img/', '../img/')
    for slug, name, rx, intro in TOPICS:
        items = [a for a in A if matches(a, rx)]
        g = "".join(fix(card(a)) for a in items) or "<p>No stories on this topic yet.</p>"
        others = " · ".join(f'<a href="{s}.html">{esc(n)}</a>' for s, n, _, _ in TOPICS if s != slug)
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{name} news", "url": f"{SITE_URL}/topics/{slug}.html",
              "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/news/{a['slug']}.html"} for i, a in enumerate(items[:30])]}}
        page(f"topics/{slug}.html", f"{name} News | Quantum Topics | PhotonDispatch", intro[:155], f'<section class="sec"><div class="w"><h1 class="sh">{esc(name)}</h1><p class="meta">{esc(intro)}</p><div class="grid">{g}</div><p class="meta" style="margin-top:24px">More topics: {others}. <a href="index.html">All topics</a>.</p></div></section>', 1, ld)
        lm = max([a.get("updated", a["date"]) for a in items] or ["2026-11-12"])
        out.append((f"topics/{slug}.html", lm, name, len(items)))
    lis = "".join(f'<li><a href="{p.split("/")[1]}">{esc(n)}</a> <span class="meta">({k} stories)</span></li>' for p, _, n, k in out)
    page("topics/index.html", "Quantum Topics | PhotonDispatch", "Follow quantum computing news by company and technology: IBM, IonQ, Quantinuum, Google, error correction, trapped ions and photonics.", f'<div class="prose page"><h1>Quantum topics</h1><p>Follow one company or technology across our coverage. Each topic page lists every matching story, newest first, with links to its sources.</p><ul>{lis}</ul></div>', 1)
    out.append(("topics/", max(d for _, d, _, _ in out), "Topics", 0))
    return out
