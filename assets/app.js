const API = 'api/v1';
const $ = (s, r = document) => r.querySelector(s);
const el = (t, c, h) => { const n = document.createElement(t); if (c) n.className = c; if (h != null) n.innerHTML = h; return n; };
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const cache = new Map();

async function get(path) {
  if (cache.has(path)) return cache.get(path);
  const r = await fetch(`${API}/${path}`);
  if (!r.ok) throw new Error(`${path} → ${r.status}`);
  const j = await r.json();
  cache.set(path, j);
  return j;
}

const brandClass = b => b === 'MINI' ? 'mini' : b === 'Rolls-Royce' ? 'rr' : 'bmw';
const dash = v => (v == null || v === '') ? '<span class="muted">—</span>' : esc(v);

/* ---------------------------------------------------------------- rendering */

function codeTable(rows, opts = {}) {
  if (!rows.length) return '<p class="empty">No production codes recorded for this chassis.</p>';
  const chassisCol = opts.chassis ? '<th>Chassis</th>' : '';
  const body = rows.map(r => `
    <tr>
      <td class="code"><a href="#/code/${encodeURIComponent(r.code)}">${esc(r.code)}</a></td>
      ${opts.chassis ? `<td><a href="#/model/${esc(r.chassis_slug)}">${esc(r.chassis)}</a></td>` : ''}
      <td>${dash(r.model)}</td>
      <td>${dash(r.body)}</td>
      <td>${r.engine_slug ? `<a href="#/engine/${esc(r.engine_slug)}">${esc(r.engine)}</a>` : dash(r.engine)}</td>
      <td>${r.power_kw ? esc(r.power_kw) + ' kW' : '<span class="muted">—</span>'}</td>
      <td>${dash(r.drivetrain)}</td>
      <td>${dash(r.steering)}</td>
      <td>${dash(r.region)}</td>
      <td>${r.from ? esc(r.from) + (r.to ? ' – ' + esc(r.to) : ' –') : '<span class="muted">—</span>'}</td>
    </tr>`).join('');
  return `<div class="tablewrap"><table>
    <thead><tr><th>Code</th>${chassisCol}<th>Model</th><th>Body</th><th>Engine</th><th>Power</th>
    <th>Drivetrain</th><th>Steering</th><th>Region</th><th>Built</th></tr></thead>
    <tbody>${body}</tbody></table></div>`;
}

async function viewHome() {
  const meta = await get('meta.json');
  const c = meta.counts;
  const stat = (n, l) => `<div class="stat"><b>${n.toLocaleString()}</b><span>${l}</span></div>`;
  return `
  <div class="hero"><div class="wrap">
    <h1>BMW chassis codes, factory type keys and engines — as open data</h1>
    <p>bimmerarchive.org is offline. This is its reference data, parsed out of Internet Archive
       snapshots into structured JSON, served as a free static API and browsable here.</p>
    <div class="stats">
      ${stat(c.models, 'chassis codes')}
      ${stat(c.production_codes, 'production codes')}
      ${stat(c.engines, 'engine variants')}
      ${stat(c.plants, 'plants')}
      ${stat(c.regions, 'market regions')}
    </div>
  </div></div>
  <div class="wrap">
    <div class="search">
      <input id="q" type="search" autocomplete="off" spellcheck="false"
             placeholder="Search a chassis code, model or engine — E30, M5 Touring, S54, AL11…">
      <p class="hint">Type a 4-character production code (e.g. <code>AL11</code>) to resolve it to an exact car.</p>
    </div>
    <div id="results"></div>

    <section>
      <h2>What this data is</h2>
      <p class="sub">Three layers, increasing in specificity.</p>
      <div class="grid">
        <a class="item" href="#/models"><b>Chassis code</b>
          <span>E30, G20, RR25 — a model generation and body.</span></a>
        <a class="item" href="#/codes"><b>Production code</b>
          <span>AL11, 1351 — BMW's internal type key. Pins down market, body, engine, steering side.</span></a>
        <a class="item" href="#/engines"><b>Engine code</b>
          <span>S54B32, B58B30M0 — displacement, output, bore and stroke.</span></a>
      </div>
      <div class="note">The production code is the layer that matters. It is the key encoded in the
        VIN, and it is what makes a VIN resolvable to an exact factory configuration.</div>
    </section>
  </div>`;
}

async function viewModels() {
  const d = await get('models.json');
  window.__models = d.results;
  return `<div class="wrap"><section>
    <h2>Chassis codes</h2>
    <p class="sub">${d.count} model generations across BMW, MINI and Rolls-Royce.</p>
    <div class="filters" id="brandFilter">
      <button class="chip on" data-b="">All</button>
      <button class="chip" data-b="BMW">BMW</button>
      <button class="chip" data-b="MINI">MINI</button>
      <button class="chip" data-b="Rolls-Royce">Rolls-Royce</button>
    </div>
    <div class="grid" id="modelGrid"></div>
  </section></div>`;
}

function paintModels(brand) {
  const g = $('#modelGrid');
  if (!g) return;
  const list = window.__models.filter(m => !brand || m.brand === brand);
  g.innerHTML = list.map(m => `
    <a class="item" href="#/model/${esc(m.slug)}">
      <b>${esc(m.code)}</b>
      <span>${esc(m.description)}</span>
      <em>${esc(m.years)} · ${m.production_code_count} code${m.production_code_count === 1 ? '' : 's'}</em>
    </a>`).join('');
}

async function viewModel(slug) {
  const m = await get(`models/${slug}.json`);
  const plants = m.plants.length
    ? m.plants.map(p => esc(p.name)).join(', ') : null;
  return `<div class="wrap"><section>
    <a class="back" href="#/models">← all chassis codes</a>
    <h2>${esc(m.code)} <span class="badge ${brandClass(m.brand)}">${esc(m.brand)}</span></h2>
    <p class="sub">${esc(m.description)}</p>
    <div class="card">
      <dl class="facts">
        <dt>Production</dt><dd>${dash(m.years)}</dd>
        <dt>Plants</dt><dd>${dash(plants)}</dd>
        <dt>Production codes</dt><dd>${m.production_codes.length}</dd>
        <dt>API</dt><dd><code>${API}/models/${esc(m.slug)}.json</code></dd>
      </dl>
    </div>
    <h3>Production codes</h3>
    ${codeTable(m.production_codes)}
  </section></div>`;
}

async function viewEngines() {
  const d = await get('engines.json');
  const fams = [...new Set(d.results.map(e => e.family))];
  const groups = fams.map(f => {
    const rows = d.results.filter(e => e.family === f).map(e => `
      <tr>
        <td class="code"><a href="#/engine/${esc(e.slug)}">${esc(e.code)}</a></td>
        <td>${e.displacement_cc ? esc(e.displacement_cc) + ' cm³' : '<span class="muted">—</span>'}</td>
        <td>${e.power_kw ? `${esc(e.power_kw)} kW (${esc(e.power_ps)} PS)` : '<span class="muted">—</span>'}</td>
        <td>${e.torque_nm ? esc(e.torque_nm) + ' Nm' : '<span class="muted">—</span>'}</td>
        <td>${dash(e.years)}</td>
      </tr>`).join('');
    return `<h3>${esc(f)}</h3><div class="tablewrap"><table>
      <thead><tr><th>Code</th><th>Displacement</th><th>Power</th><th>Torque</th><th>Built</th></tr></thead>
      <tbody>${rows}</tbody></table></div>`;
  }).join('');
  return `<div class="wrap"><section>
    <h2>Engines</h2>
    <p class="sub">${d.count} variants in ${fams.length} families.</p>
    ${groups}</section></div>`;
}

async function viewEngine(slug) {
  const e = await get(`engines/${slug}.json`);
  const bore = e.bore_mm ? `${e.bore_mm} mm × ${e.stroke_mm} mm` : null;
  // Find production codes that use this engine (via engine_slug)
  let usedIn = '';
  try {
    const pcs = await get('production-codes.json');
    const matches = pcs.results.filter(r => r.engine_slug === slug);
    if (matches.length) {
      // Group by chassis for compact display
      const byChassis = {};
      for (const m of matches) {
        const key = m.chassis || '?';
        if (!byChassis[key]) byChassis[key] = { slug: m.chassis_slug, codes: [] };
        byChassis[key].codes.push(m.code);
      }
      const rows = Object.entries(byChassis).map(([ch, v]) =>
        `<tr><td><a href="#/model/${esc(v.slug)}">${esc(ch)}</a></td>` +
        `<td>${v.codes.map(c => `<a href="#/code/${encodeURIComponent(c)}">${esc(c)}</a>`).join(', ')}</td>` +
        `<td>${v.codes.length}</td></tr>`).join('');
      usedIn = `<h3>Used in (${matches.length} production codes)</h3>
        <div class="tablewrap"><table>
        <thead><tr><th>Chassis</th><th>Codes</th><th>Count</th></tr></thead>
        <tbody>${rows}</tbody></table></div>`;
    }
  } catch { /* production-codes.json too large or missing — skip */ }
  return `<div class="wrap"><section>
    <a class="back" href="#/engines">← all engines</a>
    <h2>${esc(e.code)}</h2>
    <p class="sub">${esc(e.family)} family</p>
    <div class="card"><dl class="facts">
      <dt>Built</dt><dd>${dash(e.years)}</dd>
      <dt>Construction</dt><dd>${dash(e.construction)}</dd>
      <dt>Displacement</dt><dd>${e.displacement_cc ? esc(e.displacement_cc) + ' cm³' : dash(null)}</dd>
      <dt>Power</dt><dd>${e.power_kw ? `${esc(e.power_kw)} kW (${esc(e.power_ps)} PS)${e.power_rpm ? ' at ' + esc(e.power_rpm) + ' rpm' : ''}` : dash(null)}</dd>
      <dt>Torque</dt><dd>${e.torque_nm ? `${esc(e.torque_nm)} Nm${e.torque_rpm ? ' at ' + esc(e.torque_rpm) + ' rpm' : ''}` : dash(null)}</dd>
      <dt>Compression</dt><dd>${dash(e.compression_ratio)}</dd>
      <dt>Bore × stroke</dt><dd>${dash(bore)}</dd>
      <dt>Fuel</dt><dd>${dash(e.fuel)}</dd>
      <dt>API</dt><dd><code>${API}/engines/${esc(e.slug)}.json</code></dd>
    </dl></div>${usedIn}</section></div>`;
}

async function viewCode(code) {
  const safe = code.toUpperCase().replace(/[^A-Z0-9_-]/g, '_');
  let d;
  try { d = await get(`production-codes/${safe}.json`); }
  catch { return `<div class="wrap"><section>
      <a class="back" href="#/">← home</a>
      <h2>${esc(code)}</h2>
      <p class="empty">No production code <code>${esc(code)}</code> in this dataset.</p>
    </section></div>`; }
  return `<div class="wrap"><section>
    <a class="back" href="#/">← home</a>
    <h2>Production code ${esc(d.code)}</h2>
    <p class="sub">${d.count} matching record${d.count === 1 ? '' : 's'}.</p>
    ${codeTable(d.results, { chassis: true })}
    <div class="card" style="margin-top:16px">
      <dl class="facts"><dt>API</dt>
      <dd><code>${API}/production-codes/${esc(d.code)}.json</code></dd></dl>
    </div>
  </section></div>`;
}

async function viewCodes() {
  const meta = await get('meta.json');
  return `<div class="wrap"><section>
    <h2>Production codes</h2>
    <p class="sub">${meta.counts.production_codes.toLocaleString()} records,
       ${meta.counts.unique_production_codes.toLocaleString()} distinct keys.</p>
    <div class="search">
      <input id="codeq" type="search" autocomplete="off" spellcheck="false"
             placeholder="Enter a production code — AL11, 1351, DX71…">
      <p class="hint">Every code in this dataset resolves to exactly one factory configuration.</p>
    </div>
    <div id="codeResult"></div>
    <p class="muted">The full flat list is <code>${API}/production-codes.json</code>.
       For a single lookup use <code>${API}/production-codes/{CODE}.json</code> instead.</p>
  </section></div>`;
}

async function viewApi() {
  const meta = await get('meta.json');
  const rows = Object.entries(meta.endpoints)
    .map(([k, v]) => `<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join('');
  return `<div class="wrap"><section>
    <h2>API</h2>
    <p class="sub">Static JSON. No key, no rate limit, no server.</p>
    <div class="tablewrap"><table class="endpoints">
      <thead><tr><th>Endpoint</th><th>Returns</th></tr></thead><tbody>${rows}</tbody></table></div>

    <h3>Resolve a production code</h3>
    <pre>curl https://&lt;host&gt;/${API}/production-codes/AL11.json</pre>
    <pre>{
  "code": "AL11",
  "count": 1,
  "results": [{
    "code": "AL11", "model": "316i", "body": "Sedan",
    "engine": "M43/TU", "power_kw": 77,
    "drivetrain": "Rear-Wheel Drive", "steering": "left",
    "region": "Europe", "from": "1998-06", "to": "2001-08",
    "chassis": "E46 (4)", "chassis_slug": "e46-4", "brand": "BMW"
  }]
}</pre>

    <h3>Notes</h3>
    <ul>${meta.notes.map(n => `<li>${esc(n)}</li>`).join('')}</ul>

    <h3>Provenance</h3>
    <div class="card"><dl class="facts">
      <dt>Origin</dt><dd>${esc(meta.source.site)}</dd>
      <dt>Retrieved via</dt><dd>${esc(meta.source.retrieved_via)}</dd>
      <dt>Generated</dt><dd>${esc(meta.generated)}</dd>
      <dt>Version</dt><dd>${esc(meta.version)}</dd>
    </dl></div>
  </section></div>`;
}

/* ------------------------------------------------------------------ search */

let index = null;
async function ensureIndex() {
  if (!index) index = (await get('search.json')).results;
  return index;
}

async function runSearch(term) {
  const box = $('#results');
  if (!box) return;
  const q = term.trim().toLowerCase();
  if (!q) { box.innerHTML = ''; return; }

  if (/^[a-z0-9]{4}$/i.test(q)) {
    const safe = q.toUpperCase();
    try {
      const d = await get(`production-codes/${safe}.json`);
      box.innerHTML = `<section><h2>Production code ${esc(d.code)}</h2>
        <p class="sub">${d.count} record${d.count === 1 ? '' : 's'}</p>
        ${codeTable(d.results, { chassis: true })}</section>`;
      return;
    } catch { /* not a code — fall through to text search */ }
  }

  const idx = await ensureIndex();
  const hits = idx.filter(r =>
    r.c.toLowerCase().includes(q) || r.d.toLowerCase().includes(q)).slice(0, 60);
  box.innerHTML = hits.length
    ? `<section><h2>${hits.length} match${hits.length === 1 ? '' : 'es'}</h2><div class="grid">` +
      hits.map(r => `<a class="item" href="#/${r.t}/${esc(r.s)}">
        <b>${esc(r.c)}</b><span>${esc(r.d)}</span>
        <em>${esc(r.y)}${r.t === 'model' ? ` · ${r.n} code${r.n === 1 ? '' : 's'}` : ''}</em></a>`).join('') +
      '</div></section>'
    : '<section><p class="empty">Nothing matched.</p></section>';
}

/* ------------------------------------------------------------------ router */

const routes = [
  [/^#?\/?$/,                    viewHome],
  [/^#\/models$/,                viewModels],
  [/^#\/model\/(.+)$/,           viewModel],
  [/^#\/engines$/,               viewEngines],
  [/^#\/engine\/(.+)$/,          viewEngine],
  [/^#\/codes$/,                 viewCodes],
  [/^#\/code\/(.+)$/,            viewCode],
  [/^#\/api$/,                   viewApi],
];

async function route() {
  const h = location.hash || '#/';
  const app = $('#app');
  for (const [re, fn] of routes) {
    const m = h.match(re);
    if (!m) continue;
    app.innerHTML = '<div class="wrap"><p class="empty">Loading…</p></div>';
    try { app.innerHTML = await fn(decodeURIComponent(m[1] || '')); }
    catch (e) { app.innerHTML = `<div class="wrap"><p class="empty">Could not load: ${esc(e.message)}</p></div>`; }
    window.scrollTo(0, 0);
    document.querySelectorAll('nav.links a').forEach(a =>
      a.classList.toggle('on', a.getAttribute('href') === h));
    wire();
    return;
  }
  app.innerHTML = '<div class="wrap"><p class="empty">Not found.</p></div>';
}

function wire() {
  const q = $('#q');
  if (q) {
    let t;
    q.addEventListener('input', () => { clearTimeout(t); t = setTimeout(() => runSearch(q.value), 160); });
    q.focus();
  }
  const cq = $('#codeq');
  if (cq) {
    let t;
    cq.addEventListener('input', () => {
      clearTimeout(t);
      t = setTimeout(async () => {
        const v = cq.value.trim().toUpperCase();
        const box = $('#codeResult');
        if (v.length < 3) { box.innerHTML = ''; return; }
        try {
          const d = await get(`production-codes/${v.replace(/[^A-Z0-9_-]/g, '_')}.json`);
          box.innerHTML = codeTable(d.results, { chassis: true });
        } catch { box.innerHTML = `<p class="empty">No code <code>${esc(v)}</code>.</p>`; }
      }, 200);
    });
    cq.focus();
  }
  const bf = $('#brandFilter');
  if (bf) {
    paintModels('');
    bf.addEventListener('click', ev => {
      const b = ev.target.closest('.chip');
      if (!b) return;
      bf.querySelectorAll('.chip').forEach(c => c.classList.toggle('on', c === b));
      paintModels(b.dataset.b);
    });
  }
}

$('#theme').addEventListener('click', () => {
  const cur = document.documentElement.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  try { localStorage.setItem('theme', next); } catch {}
});
try {
  const saved = localStorage.getItem('theme');
  if (saved) document.documentElement.setAttribute('data-theme', saved);
} catch {}

window.addEventListener('hashchange', route);
route();
