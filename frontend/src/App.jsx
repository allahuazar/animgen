import { useState, useEffect } from 'react'

function App() {
  const [prompt, setPrompt] = useState('Animate plotting the point x = 7 on a number line.')
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(null)
  const [error, setError] = useState(null)
  const [routerResult, setRouterResult] = useState(null)
  const [snippets, setSnippets] = useState(null)
  const [generatedCode, setGeneratedCode] = useState(null)
  const [warnings, setWarnings] = useState(null)
  const [renderResult, setRenderResult] = useState(null)
  const [videoUrl, setVideoUrl] = useState(null)
  const [repaired, setRepaired] = useState(null)

  useEffect(() => {
    fetch('/health').then(r => r.json()).then(d => setHealth(d.ok ? 'ok' : 'err')).catch(() => setHealth('err'))
  }, [])

  async function doRoute() {
    setLoading('route'); setError(null); setRouterResult(null)
    try {
      const r = await fetch('/route', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({prompt}) })
      const d = await r.json()
      d.ok ? setRouterResult(d) : setError(d.error)
    } catch { setError('Route request failed') }
    setLoading(null)
  }

  async function doSearch() {
    setLoading('search'); setError(null); setSnippets(null)
    try {
      const r = await fetch('/search-manim-docs', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({queries: [prompt]}) })
      const d = await r.json()
      d.ok ? setSnippets(d) : setError(d.error)
    } catch { setError('Search request failed') }
    setLoading(null)
  }

  async function doGenerate() {
    setLoading('generate'); setError(null); setGeneratedCode(null); setWarnings(null); setRouterResult(null); setSnippets(null)
    try {
      const r = await fetch('/generate-manim', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({prompt}) })
      const d = await r.json()
      if (d.ok) { setRouterResult(d.router); setSnippets({snippets: d.snippets, count: d.snippets.length}); setGeneratedCode(d.code); setWarnings(d.warnings) }
      else setError(d.error)
    } catch { setError('Generate request failed') }
    setLoading(null)
  }

  async function doRender() {
    setLoading('render'); setError(null); setRenderResult(null); setVideoUrl(null)
    try {
      const r = await fetch('/render-manim', { method: 'POST' })
      const d = await r.json()
      if (d.ok) { setRenderResult(d); setVideoUrl(d.video_url) }
      else setError(d.error)
    } catch { setError('Render request failed') }
    setLoading(null)
  }

  async function doFull() {
    setLoading('full'); setError(null); setRouterResult(null); setSnippets(null); setGeneratedCode(null); setWarnings(null); setRenderResult(null); setVideoUrl(null); setRepaired(null)
    try {
      const r = await fetch('/generate-and-render-manim', { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({prompt}) })
      const d = await r.json()
      if (d.ok) {
        setRouterResult(d.router)
        setGeneratedCode(d.code)
        setWarnings(d.warnings)
        setRenderResult(d.render)
        setVideoUrl(d.video_url)
        setRepaired(d.repaired)
      } else setError(d.error)
    } catch { setError('Full workflow request failed') }
    setLoading(null)
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Animgen</h1>
        <span className={`health health--${health === 'ok' ? 'ok' : 'err'}`}>
          {health === 'ok' ? 'API connected' : health || 'checking\u2026'}
        </span>
      </header>

      <section className="card">
        <label className="label">Prompt</label>
        <textarea className="input input--prompt" rows={3} value={prompt} onChange={e => setPrompt(e.target.value)} placeholder="Describe the animation you want\u2026" />
        <div className="actions">
          <button onClick={doRoute} disabled={loading}>{loading === 'route' ? 'Routing\u2026' : 'Route'}</button>
          <button onClick={doSearch} disabled={loading}>{loading === 'search' ? 'Searching\u2026' : 'Search Docs'}</button>
          <button onClick={doGenerate} disabled={loading}>{loading === 'generate' ? 'Generating\u2026' : 'Generate Code'}</button>
          <button onClick={doRender} disabled={loading}>{loading === 'render' ? 'Rendering\u2026' : 'Render'}</button>
          <button className="btn-primary" onClick={doFull} disabled={loading}>{loading === 'full' ? 'Working\u2026' : 'Generate + Render'}</button>
        </div>
        {error && <p className="error">{error}</p>}
      </section>

      {routerResult && (
        <section className="card">
          <h2 className="card-title">Router</h2>
          <pre className="block">{JSON.stringify(routerResult, null, 2)}</pre>
        </section>
      )}

      {snippets && (
        <section className="card">
          <h2 className="card-title">Docs Snippets ({snippets.count || 0})</h2>
          {snippets.snippets?.slice(0, 3).map((s, i) => (
            <pre key={i} className="block block--small">{s.source}<br />{s.snippet.slice(0, 500)}</pre>
          ))}
          {snippets.count > 3 && <p className="muted">+{snippets.count - 3} more</p>}
        </section>
      )}

      {generatedCode && (
        <section className="card">
          <h2 className="card-title">Generated Code</h2>
          <textarea className="input input--code" rows={12} value={generatedCode} readOnly />
        </section>
      )}

      {warnings && warnings.length > 0 && (
        <section className="card card--warning">
          <h2 className="card-title">Layout Warnings</h2>
          {warnings.map((w, i) => <p key={i} className="warning-item">{w}</p>)}
        </section>
      )}

      {videoUrl && (
        <section className="card">
          <h2 className="card-title">Video</h2>
          <video src={`/${videoUrl}`} controls className="video" />
        </section>
      )}

      {renderResult && (
        <section className="card">
          <h2 className="card-title">Render {repaired !== null && <span className="badge">{repaired ? 'Repaired' : 'First try'}</span>}</h2>
          <div className="render-meta">
            <span>OK: {renderResult.ok ? '\u2705' : '\u274c'}</span>
            {renderResult.video_url && <span> Video: <a href={`/${renderResult.video_url}`}>{renderResult.video_url.split('/').pop()}</a></span>}
          </div>
          {renderResult.stdout && (
            <details>
              <summary>stdout</summary>
              <pre className="block block--small">{renderResult.stdout.slice(-3000)}</pre>
            </details>
          )}
          {renderResult.stderr && (
            <details>
              <summary>stderr</summary>
              <pre className="block block--small block--err">{renderResult.stderr.slice(-2000)}</pre>
            </details>
          )}
        </section>
      )}
    </div>
  )
}

export default App
