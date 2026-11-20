"""Topic hubs for PhotonDispatch (added 12 Nov 2026).
Each hub collects every published article whose title or summary matches the topic, newest first,
so readers and crawlers can follow one company or technology across stories. Rebuilt on every build.py run."""
import re
TOPICS = [
 ("ibm", "IBM", r"\bibm\b", "Every PhotonDispatch story about IBM's quantum computing work: processors, roadmaps, partnerships and research, each linked to its sources."),
 ("ionq", "IonQ", r"\bionq\b", "Every PhotonDispatch story about IonQ: trapped ion systems, deals, acquisitions and company announcements, each linked to its sources."),
 ("quantinuum", "Quantinuum", r"quantinuum", "Every PhotonDispatch story about Quantinuum: trapped ion hardware, error correction results and company news, each linked to its sources."),
 ("google-quantum-ai", "Google Quantum AI", r"\bgoogle\b", "Google says Willow has 105 qubits. DARPA's 8 Oct 2026 list still places Google Quantum AI in Stage A."),
 ("error-correction", "Quantum error correction", r"error.correct|logical qubit|decod", "Stories on quantum error correction: logical qubits, decoders and fault tolerance results, each linked to its sources. Company claims are attributed as such."),
 ("trapped-ions", "Trapped ion quantum computing", r"trapped.ion|\bionq\b|quantinuum", "Stories on trapped ion quantum computers, which use individual charged atoms held in electromagnetic traps as qubits, each linked to its sources."),
 ("photonic", "Photonic quantum computing", r"photonic|psiquantum", "Stories on photonic quantum computing, which uses particles of light as qubits, each linked to its sources."),
]
def matches(a, rx): return re.search(rx, (a["title"] + " " + a["summary"]).lower()) is not None
def topics_for(a): return [(s, n) for s, n, rx, _ in TOPICS if matches(a, rx)]

def _by_slug(A):
    return {a["slug"]: a for a in A}

def google_essay():
    """Substantive hub copy. Figures are from pages opened 20 Nov 2026, or are carried from a sourced story on this site and labelled that way."""
    return """<div class="hubcopy">
<p class="lede"><strong>Short answer:</strong> Google Quantum AI is the quantum computing group Hartmut Neven says he founded in 2012 inside Google Research. Its processor Willow has 105 qubits, according to <a href="https://blog.google/technology/research/google-willow-quantum-chip/" rel="noopener">Google's 9 December 2024 announcement</a> (that page says it was last updated 12 June 2025). The same post is where Google sets out Willow's error-correction and benchmark claims. Those blog figures were checked again on 20 November 2026.</p>
<h2>What Google says the lab is</h2>
<p>Neven writes that the aim was a useful, large-scale quantum computer, and that Willow was made in a Santa Barbara facility built for chips of this kind. He also places the group inside Google Research. This page has no independent visit to that lab. The description is Google's.</p>
<h2>What Google says Willow did</h2>
<p>The announcement says the team ran memories on grids of 3 by 3, 5 by 5 and 7 by 7 encoded qubits, and that each step up cut the error rate in half. Google calls that below threshold: the error rate fell as the code grew, which is the behaviour error correction needs, rather than extra qubits only adding noise. Google also says the encoded groups lasted longer than the best single physical qubits on the chip, a comparison it calls beyond breakeven. <a href="../news/what-is-a-logical-qubit.html">What a logical qubit is</a> explains why that comparison is the one that matters, and <a href="../news/quantum-error-correction-basics.html">quantum error correction basics</a> defines the threshold. The sharper per-cycle percentages in those explainers come from the group's Nature paper, not from the blog post opened for this page, so they are not repeated here.</p>
<p>Google says Willow's T1 times, how long a qubit holds an excitation, are approaching 100 microseconds, about five times its previous chips. That, too, is Google's figure from the same post.</p>
<p>On random circuit sampling, Google says Willow finished a run in under five minutes that would take the Frontier supercomputer 10 to the power of 25 years. Google says the estimate gives Frontier full use of its disks, which Google itself calls a generous assumption, and that classical computers should be expected to get better at the same test. Google also says the test has no known commercial use. The post's own next aim is a calculation that is both out of reach for classical computers and useful for something. A 105-qubit count and a large sampling gap are not that result.</p>
<h2>Two later Willow reports on this site</h2>
<p>Our <a href="../news/google-magic-state-cultivation-willow-science.html">15 October report</a> covers Google's claim that magic state cultivation ran on Willow. Our <a href="../news/google-willow-contextuality-magic-square-game-98-percent-105-qubits-science.html">20 November story</a>, citing Google's research blog and a Science paper, reports Google's figure of 98.3 percent of rounds won on the magic square game against a classical ceiling of 88.9 percent, using up to 105 qubits. That story says Google does not present the result as useful quantum advantage. The 98.3 percent figure was not re-opened in the Science PDF for this hub. It is carried from that sourced story.</p>
<h2>Where a government list puts the group</h2>
<p><a href="https://www.darpa.mil/research/programs/quantum-benchmarking-initiative" rel="noopener">DARPA's Quantum Benchmarking Initiative page</a>, whose performer list is marked current as of 8 October 2026, places Google Quantum AI in Stage A, on superconducting transmon qubits. On that page Stage A is the step where a team describes a utility-scale concept, and the award ceiling listed for it is $1 million. The same list puts <a href="ionq.html">IonQ</a>, IBM, Atom Computing, Diraq, Microsoft and PsiQuantum in Stage C, where the ceiling listed is $300 million. <a href="quantinuum.html">Quantinuum</a> is in Stage B. DARPA says a company is listed only while it has an active scope of work, and that the list is not updated in real time, so Stage A on that date is not a published verdict that Google cannot go further.</p>
<p>The cards further down also include Google DeepMind items, because this hub collects stories that mention Google. The <a href="../news/google-lean-4-verified-quantum-algorithms.html">Lean 4 algorithm note</a> and the <a href="../news/deepmind-rsa-1024-ai-cryptanalysis.html">1024-bit RSA note</a> are DeepMind write-ups, not Willow chip benchmarks.</p>
<aside class="compare"><h2>Check another</h2><ul>
<li><a href="ibm.html">IBM</a>, which DARPA's 8 October 2026 list places in Stage C on modular superconducting processors.</li>
<li><a href="ionq.html">IonQ</a>, the trapped-ion company on that same Stage C list.</li>
<li><a href="../news/what-is-a-logical-qubit.html">What a logical qubit is</a>, for the vocabulary behind Willow's error-correction claim.</li>
<li><a href="../news/quantum-error-correction-basics.html">Quantum error correction basics</a>, including the threshold idea Google is invoking.</li>
</ul></aside>
<p class="meta">Last verified 20 November 2026 against Google's Willow announcement and DARPA's program page. The November contextuality percentage is as reported in our story from that day.</p>
<div class="src"><h2>Sources</h2><ul>
<li><a href="https://blog.google/technology/research/google-willow-quantum-chip/" rel="noopener">Google, Hartmut Neven: Meet Willow, our state-of-the-art quantum chip (9 December 2024, page updated 12 June 2025; checked 20 November 2026)</a></li>
<li><a href="https://www.darpa.mil/research/programs/quantum-benchmarking-initiative" rel="noopener">DARPA: Quantum Benchmarking Initiative, performer list current as of 8 October 2026 (checked 20 November 2026)</a></li>
<li><a href="../news/google-willow-contextuality-magic-square-game-98-percent-105-qubits-science.html">PhotonDispatch, 20 November 2026: Google's contextuality result on Willow, with that story's own sources</a></li>
</ul></div>
</div>"""

def build(A, page, card, esc, SITE_URL, widgets):
    out = []
    fix = lambda h: h.replace('href="news/', 'href="../news/').replace('href="category/', 'href="../category/').replace('img/', '../img/').replace('../../img/', '../img/')
    by_slug = _by_slug(A)
    crumbs = widgets["crumbs"]
    crumb_ld = widgets["crumb_ld"]
    nextreads = widgets["nextreads"]
    for slug, name, rx, intro in TOPICS:
        items = [a for a in A if matches(a, rx)]
        g = "".join(fix(card(a)) for a in items) or "<p>No stories on this topic yet.</p>"
        others = [(s, n) for s, n, _, _ in TOPICS if s != slug]
        # A lookup page gets a real "check another" box, not a second copy of the story grid.
        compare_links = others[:3]
        compare = '<aside class="compare"><h2>Check another</h2><ul>' + "".join(
            f'<li><a href="{s}.html">{esc(n)}</a></li>' for s, n in compare_links) + "</ul></aside>"
        url = f"{SITE_URL}/topics/{slug}.html"
        nav = crumbs([("../index.html", "Home"), ("index.html", "Topics"), (None, name)])
        byline = '<p class="byline">By <a rel="author" href="../about.html">PhotonDispatch Staff</a></p>'
        essay = ""
        mid = ""
        end = ""
        if slug == "google-quantum-ai":
            essay = google_essay()
            want = [
                "google-willow-contextuality-magic-square-game-98-percent-105-qubits-science",
                "google-magic-state-cultivation-willow-science",
                "what-is-a-logical-qubit",
                "quantum-error-correction-basics",
            ]
            more = [
                "ibm-quantum-nighthawk-r3-520-qubits",
                "quantinuum-helios-99-9995-logical-fidelity-color-code",
                "ionq-q3-2026-record-revenue-guidance",
                "google-lean-4-verified-quantum-algorithms",
            ]
            mid_picks = [by_slug[s] for s in want if s in by_slug]
            end_picks = [by_slug[s] for s in more if s in by_slug]
            # nextreads expects link_prefix relative to the current page. From /topics/, news lives at ../news/.
            mid = nextreads(mid_picks, "Related reading", "../news/", "../")
            end = nextreads(end_picks, "Read next", "../news/", "../")
            # The essay already has its own compare box. Don't stack a second generic one.
            compare = ""
        else:
            # Still offer three sibling hubs. The story grid below is the archive, not a substitute for the box.
            pass
        archive = f'<h2 class="sh">All stories</h2><div class="grid">{g}</div>'
        more_line = " · ".join(f'<a href="{s}.html">{esc(n)}</a>' for s, n in others)
        heading = "What has Google Quantum AI published about Willow?" if slug == "google-quantum-ai" else name
        body = (f'<section class="sec"><div class="w">{nav}{byline}<h1>{esc(heading)}</h1>'
                f'<div class="prose" style="max-width:740px;margin:0;padding:0">{essay}{mid}{compare}{end}</div>'
                f'{archive}<p class="meta" style="margin-top:24px">More topics: {more_line}. <a href="index.html">All topics</a>.</p></div></section>')
        desc = intro if len(intro) <= 155 else intro[:152].rsplit(" ", 1)[0] + "..."
        title = f"What has Google Quantum AI published about Willow? | PhotonDispatch" if slug == "google-quantum-ai" else f"{name} News | Quantum Topics | PhotonDispatch"
        ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": name if slug != "google-quantum-ai" else "What has Google Quantum AI published about Willow?",
              "url": url, "author": {"@type": "Organization", "name": "PhotonDispatch Staff", "url": SITE_URL + "/about.html"},
              "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f"{SITE_URL}/news/{a['slug']}.html"} for i, a in enumerate(items[:30])]}}
        bld = crumb_ld([(SITE_URL + "/", "Home"), (SITE_URL + "/topics/", "Topics"), (url, name)])
        page(f"topics/{slug}.html", title, desc, body, 1, [ld, bld])
        lm = max([a.get("updated", a["date"]) for a in items] or ["2026-11-12"])
        out.append((f"topics/{slug}.html", lm, name, len(items)))
    lis = "".join(f'<li><a href="{p.split("/")[1]}">{esc(n)}</a> <span class="meta">({k} stories)</span></li>' for p, _, n, k in out)
    idx_nav = crumbs([("../index.html", "Home"), (None, "Topics")])
    idx_ld = crumb_ld([(SITE_URL + "/", "Home"), (SITE_URL + "/topics/", "Topics")])
    page("topics/index.html", "Quantum Topics | PhotonDispatch", "Follow quantum computing news by company and technology: IBM, IonQ, Quantinuum, Google, error correction, trapped ions and photonics.",
         f'<div class="prose page">{idx_nav}<p class="byline">By <a rel="author" href="../about.html">PhotonDispatch Staff</a></p><h1>Quantum topics</h1><p>Follow one company or technology across our coverage. Each topic page lists every matching story, newest first, with links to its sources.</p><ul>{lis}</ul></div>', 1, idx_ld)
    out.append(("topics/", max(d for _, d, _, _ in out), "Topics", 0))
    return out
