#!/usr/bin/env python3
"""Adds the Professor Okafor tab to index.html (run once; safe to re-run).

The tab lists and plays the videos in ./videos, served by surgeonary_server.py,
and pops up new uploads from the Pi camera as they arrive.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "index.html")

NAV_ANCHOR = '<span class="t">Video library selection</span></button>'
NAV_ADD = (
    '\n        <button type="button" data-go="okafor"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" '
    'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="7.5" cy="6.5" r="3"/>'
    '<path d="M2 16.5c.6-3 2.7-4.7 5.5-4.7 1.6 0 3 .6 4 1.6"/><rect x="12" y="10.5" width="5" height="4" rx="1"/>'
    '<path d="M17 12.5l2-1.2v2.4z"/></svg><span class="t">Professor Okafor</span>'
    '<span class="tagx" id="navOkafor" hidden></span></button>'
)

PAGES_ANCHOR = "profile:{ name:'Profile', eyebrow:'Account', keys:'dr okafor' }"
PAGES_ADD = (", okafor:{ name:'Professor Okafor', eyebrow:'Platform', "
             "keys:'professor okafor videos uploads recordings camera wearable' }")

HASH_ANCHOR = "const HASH = { home:'home',"
HASH_ADD = " okafor:'okafor', professor:'okafor',"

GO_ANCHOR = "else if (id === 'profile') renderProfile();"
GO_ADD = " else if (id === 'okafor' && window.SurgeonaryOkafor) window.SurgeonaryOkafor.show();"

SECTION_ANCHOR = '<section class="view fill" id="v-dash"'
SECTION = '''<!-- Professor Okafor: recordings uploaded from the Pi head camera (served from ./videos) -->
    <section class="view" id="v-okafor" aria-label="Professor Okafor" hidden>
      <div class="ok-wrap">
        <section class="card ok-head">
          <div class="ok-av" aria-hidden="true">PO</div>
          <div class="ok-id">
            <div class="eyebrow">Attending surgeon &middot; head-camera recordings</div>
            <h2>Professor Okafor</h2>
            <p>Cases filmed from Professor Okafor&rsquo;s point of view with the Surgeon Wearable. New recordings appear here as soon as they are uploaded from the camera.</p>
          </div>
          <div class="ok-sync" role="status"><span class="ok-dot" id="okDot"></span><span id="okSync">Checking for the camera&hellip;</span></div>
        </section>
        <section class="card ok-player" id="okPlayer" hidden>
          <video id="okVideo" controls playsinline preload="metadata"></video>
          <div class="ok-meta"><h3 id="okTitle"></h3><p id="okSub"></p></div>
        </section>
        <div class="ok-grid" id="okGrid" aria-label="Professor Okafor's recordings"></div>
        <div class="empty" id="okEmpty" hidden>
          <p>No recordings yet. Record on the Pi camera, open its <b>Video library</b> and press <b>Upload</b>. The video will appear here.</p>
        </div>
      </div>
    </section>

    '''

STYLE = '''<style id="okafor-style">
.ok-wrap{display:grid;gap:18px;max-width:1240px}
.ok-head{display:flex;gap:18px;align-items:center;flex-wrap:wrap;padding:20px 22px}
.ok-av{flex:none;width:64px;height:64px;border-radius:50%;display:grid;place-items:center;background:var(--teal-wash);border:1px solid rgba(95,211,198,.4);color:var(--teal);font-size:22px;font-weight:600;letter-spacing:.02em}
.ok-id{flex:1;min-width:240px}
.ok-id h2{margin:6px 0 4px;font-size:22px;font-weight:600}
.ok-id p{margin:0;max-width:62ch;color:var(--ink-dim);font-size:14px;line-height:1.5}
.ok-sync{display:flex;align-items:center;gap:9px;font-size:12.5px;color:var(--ink-dim);max-width:340px}
.ok-dot{flex:none;width:9px;height:9px;border-radius:50%;background:var(--ink-faint)}
.ok-dot.on{background:var(--teal);box-shadow:0 0 0 4px var(--teal-wash)}
.ok-dot.wait{background:#f5a524;box-shadow:0 0 0 4px rgba(245,165,36,.15)}
.ok-player{padding:14px;display:grid;gap:12px}
.ok-player video{width:100%;max-height:68vh;border-radius:12px;background:#000;display:block}
.ok-meta h3{margin:0;font-size:17px;font-weight:600}
.ok-meta p{margin:4px 0 0;color:var(--ink-dim);font-size:13px}
.ok-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
.ok-card{all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--panel);transition:border-color .2s,transform .2s}
.ok-card:hover{border-color:var(--hair);transform:translateY(-2px)}
.ok-card.on{border-color:var(--teal)}
.ok-card:focus-visible{outline:2px solid var(--teal);outline-offset:2px}
.ok-thumb{position:relative;display:block;aspect-ratio:16/10;background:#000}
.ok-thumb video{width:100%;height:100%;object-fit:cover;display:block;pointer-events:none}
.ok-new{position:absolute;top:8px;left:8px}
.ok-play{position:absolute;right:8px;bottom:8px;width:30px;height:30px;border-radius:50%;display:grid;place-items:center;background:rgba(0,0,0,.6);color:#fff;font-size:11px}
.ok-ct{display:grid;gap:3px;padding:10px 12px 12px}
.ok-ct b{font-size:14px;font-weight:500}
.ok-ct span{font-size:12px;color:var(--ink-faint)}
.ok-toast{position:fixed;right:20px;bottom:20px;z-index:80;display:flex;align-items:center;gap:12px;padding:12px 12px 12px 16px;border-radius:14px;background:var(--raise);border:1px solid rgba(95,211,198,.45);box-shadow:0 18px 44px rgba(0,0,0,.45);color:var(--ink);font-size:14px;opacity:0;transform:translateY(16px);pointer-events:none;transition:opacity .3s,transform .3s}
.ok-toast.show{opacity:1;transform:none;pointer-events:auto}
.ok-toast b{font-weight:600}
@media (max-width:640px){.ok-sync{max-width:none}.ok-toast{left:16px;right:16px}}
</style>
'''

TOAST = '''<div class="ok-toast" id="okToast" role="status" aria-live="polite"><span><b>New recording</b> from Professor Okafor</span><button type="button" class="btn sm teal" id="okToastGo">Watch</button></div>
'''

SCRIPT = r'''<script id="okafor-script">
/* Professor Okafor tab: lists ./videos (via surgeonary_server.py) and pops up new uploads from the Pi camera. */
(function(){
  const $ = s => document.querySelector(s);
  const grid = $('#okGrid'), empty = $('#okEmpty'), syncText = $('#okSync'), dot = $('#okDot'), badge = $('#navOkafor');
  const player = $('#okPlayer'), video = $('#okVideo'), title = $('#okTitle'), sub = $('#okSub'), toast = $('#okToast');
  if (!grid) return;
  let videos = [], known = null, current = null, sig = '', toastName = null, toastTimer = 0;
  const fresh = new Set();
  let seen; try { seen = new Set(JSON.parse(localStorage.getItem('okaforSeen') || '[]')); } catch (e) { seen = new Set(); }
  const saveSeen = () => { try { localStorage.setItem('okaforSeen', JSON.stringify(Array.from(seen))); } catch (e) {} };
  const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]));
  const mb = b => (b / 1048576).toFixed(1) + ' MB';
  const ago = t => { const s = Math.max(0, Date.now() / 1000 - t); return s < 60 ? 'just now' : s < 3600 ? Math.round(s / 60) + ' min ago' : s < 86400 ? Math.round(s / 3600) + ' h ago' : new Date(t * 1000).toLocaleDateString(); };
  const onTab = () => !!(window.__platform && window.__platform.state.view === 'okafor');

  function render(){
    if (!videos.length){ grid.innerHTML = ''; empty.hidden = false; player.hidden = true; return; }
    empty.hidden = true;
    grid.innerHTML = videos.map(v =>
      '<button type="button" class="ok-card' + (v.name === current ? ' on' : '') + '" data-name="' + esc(v.name) + '">' +
        '<span class="ok-thumb"><video src="' + esc(v.url) + '#t=0.5" preload="metadata" muted playsinline></video>' +
        (fresh.has(v.name) ? '<span class="tagx ok-new">NEW</span>' : '') + '<span class="ok-play" aria-hidden="true">&#9654;</span></span>' +
        '<span class="ok-ct"><b>' + esc(v.title) + '</b><span>' + ago(v.mtime) + ' &middot; ' + mb(v.size) + '</span></span>' +
      '</button>').join('');
  }

  function select(name, play){
    const v = videos.find(x => x.name === name); if (!v) return;
    current = v.name; player.hidden = false;
    if (video.getAttribute('src') !== v.url) video.src = v.url;
    title.textContent = v.title; sub.textContent = 'Uploaded ' + ago(v.mtime) + ' · ' + mb(v.size);
    $$cards().forEach(c => c.classList.toggle('on', c.dataset.name === current));
    if (play){ const p = video.play(); if (p && p.catch) p.catch(() => {}); }
  }
  const $$cards = () => Array.prototype.slice.call(grid.querySelectorAll('.ok-card'));

  function updateBadge(){
    const n = onTab() ? 0 : videos.filter(v => !seen.has(v.name)).length;
    badge.hidden = n === 0; badge.textContent = n + ' new';
  }

  function showToast(name){
    toastName = name; toast.classList.add('show');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => toast.classList.remove('show'), 9000);
  }

  function setSync(state, text){ dot.className = 'ok-dot' + (state ? ' ' + state : ''); syncText.textContent = text; }

  async function poll(){
    let data;
    try {
      const r = await fetch('/api/okafor/videos', { cache:'no-store' });
      if (!r.ok) throw new Error(r.status);
      data = await r.json();
    } catch (e) {
      setSync('', 'Open Surgeonary with start-surgeonary.bat to receive videos from the camera.');
      return;
    }
    const s = data.sync || {};
    if (s.downloading) setSync('on', 'Receiving a new recording from the camera…');
    else if (s.pi_reachable) setSync('on', 'Connected to the camera. Uploads appear here automatically.');
    else setSync('wait', 'Waiting for the Pi camera app at ' + (s.pi_url || 'the Pi') + '.');

    videos = data.videos || [];
    const names = videos.map(v => v.name);
    const arrived = known ? names.filter(n => !known.has(n)) : [];
    known = new Set(names);
    arrived.forEach(n => fresh.add(n));
    if (onTab()) { names.forEach(n => seen.add(n)); saveSeen(); }
    const nextSig = names.join('|') + '#' + Array.from(fresh).join('|');
    if (nextSig !== sig){ sig = nextSig; render(); }
    if (current && !known.has(current)){ current = null; video.removeAttribute('src'); player.hidden = true; }
    if (arrived.length){
      const newest = arrived[0];
      if (onTab()){ if (video.paused) select(newest, false); }
      showToast(newest);
    } else if (!current && videos.length && onTab()){
      select(videos[0].name, false);
    }
    updateBadge();
  }

  grid.addEventListener('click', e => { const c = e.target.closest('.ok-card'); if (c) { select(c.dataset.name, true); player.scrollIntoView({ behavior:'smooth', block:'nearest' }); } });
  $('#okToastGo').addEventListener('click', () => {
    toast.classList.remove('show');
    if (window.__platform) window.__platform.go('okafor');
    if (toastName) select(toastName, true);
  });

  window.SurgeonaryOkafor = {
    show(){
      videos.forEach(v => seen.add(v.name)); saveSeen(); updateBadge();
      if (!current && videos.length) select(videos[0].name, false);
      poll();
    },
    poll
  };
  poll();
  setInterval(poll, 2500);
})();
</script>
'''


def insert_after(text, anchor, add):
    assert text.count(anchor) == 1, "anchor not found exactly once: %r" % anchor[:60]
    return text.replace(anchor, anchor + add, 1)


def insert_before(text, anchor, add):
    assert text.count(anchor) == 1, "anchor not found exactly once: %r" % anchor[:60]
    return text.replace(anchor, add + anchor, 1)


def main():
    with open(PATH, encoding="utf-8") as f:
        html = f.read()
    if 'id="v-okafor"' in html:
        print("index.html already has the Professor Okafor tab; nothing to do.")
        return 0
    html = insert_after(html, NAV_ANCHOR, NAV_ADD)
    html = insert_after(html, PAGES_ANCHOR, PAGES_ADD)
    html = insert_after(html, HASH_ANCHOR, HASH_ADD)
    html = insert_after(html, GO_ANCHOR, GO_ADD)
    html = insert_before(html, SECTION_ANCHOR, SECTION)
    html = insert_before(html, "</head>", STYLE)
    assert html.count("</body>") == 1
    html = html.replace("</body>", TOAST + SCRIPT + "</body>", 1)
    with open(PATH, "w", encoding="utf-8", newline="") as f:
        f.write(html)
    print("Added the Professor Okafor tab to index.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
