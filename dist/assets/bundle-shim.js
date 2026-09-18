/* Serves the per-record API endpoints out of three bundle files, so the page
   works on hosts that cap the number of supporting files. Installed before
   app.js; app.js is unchanged. */
(function () {
  const B = {};
  const load = p => fetch('bundle/' + p).then(r => r.json());
  const ready = Promise.all([
    load('meta.json').then(d => B['meta.json'] = B['index.json'] = d),
    load('models.json').then(d => B['models.json'] = d),
    load('engines.json').then(d => B['engines.json'] = d),
    load('search.json').then(d => B['search.json'] = d),
    load('models-detail.json').then(d => B.models = d),
    load('engines-detail.json').then(d => B.engines = d),
    load('codes.json').then(d => B.codes = d),
  ]);
  const real = window.fetch.bind(window);
  window.fetch = async function (url, opts) {
    const u = String(url);
    const m = u.match(/^api\/v1\/(.+)\.json$/);
    if (!m) return real(url, opts);
    await ready;
    const key = m[1];
    let hit = B[key + '.json'];
    if (!hit) {
      const parts = key.split('/');
      if (parts.length === 2) {
        const group = parts[0] === 'production-codes' ? 'codes' : parts[0];
        hit = B[group] && B[group][parts[1]];
      }
    }
    if (hit) return new Response(JSON.stringify(hit), { status: 200 });
    return new Response('not found', { status: 404 });
  };
})();
