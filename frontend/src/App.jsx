import { useState, useEffect, useCallback } from 'react'
import './App.css'

const DEFAULT_LESSON = {
  title: 'Photosynthesis',
  subject: 'Biology',
  grade: 'Class 8',
  summary: 'Photosynthesis is the process by which green plants make their own food using sunlight, carbon dioxide, and water.',
  key_points: [
    'Plants use chlorophyll to absorb sunlight.',
    'Carbon dioxide enters the leaf through stomata.',
    'Water is absorbed by the roots and transported to the leaves.',
    'The plant produces glucose as food.',
    'Oxygen is released as a by-product.',
  ],
  formula: '6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂',
  quiz: [
    { question: 'What is the green pigment in leaves called?', answer: 'Chlorophyll' },
    { question: 'Which gas is released during photosynthesis?', answer: 'Oxygen' },
    { question: 'What food does the plant produce?', answer: 'Glucose' },
  ],
}

function Section({ title, children }) {
  return (
    <div className="section">
      <h2 className="section-title">{title}</h2>
      {children}
    </div>
  )
}

function App() {
  const [health, setHealth] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [mdFiles, setMdFiles] = useState([])
  const [mdContent, setMdContent] = useState('')
  const [selectedMd, setSelectedMd] = useState('')
  const [lessonJson, setLessonJson] = useState(JSON.stringify(DEFAULT_LESSON, null, 2))
  const [lessonError, setLessonError] = useState(null)
  const [rendering, setRendering] = useState(null)
  const [renderResult, setRenderResult] = useState(null)
  const [fileList, setFileList] = useState(null)
  const [tab, setTab] = useState('upload')
  const [aiPrompt, setAiPrompt] = useState('')
  const [groqKey, setGroqKey] = useState('')
  const [showGroqKey, setShowGroqKey] = useState(false)

  useEffect(() => {
    fetch('/health').then(r => r.json()).then(d => setHealth(d.status)).catch(() => setHealth('error'))
    fetchFiles()
  }, [])

  function fetchFiles() {
    fetch('/files').then(r => r.json()).then(d => { if (d.ok) setFileList(d) }).catch(() => {})
  }

  function fetchMdFiles() {
    fetch('/markdown').then(r => r.json()).then(d => { if (d.ok) setMdFiles(d.files) }).catch(() => {})
  }

  const uploadPdf = useCallback(async (file) => {
    setUploading(true)
    setUploadResult(null)
    const form = new FormData()
    form.append('file', file)
    try {
      const res = await fetch('/upload-pdf', { method: 'POST', body: form })
      const data = await res.json()
      setUploadResult(data)
      if (data.ok) {
        fetchMdFiles()
        setSelectedMd(data.markdown_file || '')
        setMdContent(data.markdown || '')
      }
    } catch { setUploadResult({ ok: false, error: 'Upload failed' }) }
    setUploading(false)
  }, [])

  const loadMarkdown = useCallback(async (filename) => {
    setSelectedMd(filename)
    const res = await fetch(`/markdown?filename=${encodeURIComponent(filename)}`)
    const data = await res.json()
    if (data.ok) setMdContent(data.content || '')
  }, [])

  const validateLesson = useCallback(() => {
    try {
      const parsed = JSON.parse(lessonJson)
      setLessonError(null)
      return parsed
    } catch (e) {
      setLessonError('Invalid JSON: ' + e.message)
      return null
    }
  }, [lessonJson])

  const saveLesson = useCallback(async () => {
    const parsed = validateLesson()
    if (!parsed) return
    const res = await fetch('/lesson-json', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(parsed) })
    const data = await res.json()
    if (data.ok) alert('Lesson saved!')
    else alert('Error: ' + (data.error || 'unknown'))
  }, [lessonJson, validateLesson])

  const renderTypst = useCallback(async () => {
    const parsed = validateLesson()
    if (!parsed) return
    setRendering('typst')
    setRenderResult(null)
    const res = await fetch('/render/typst', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(parsed) })
    const data = await res.json()
    setRenderResult(data)
    setRendering(null)
    if (data.ok) fetchFiles()
  }, [lessonJson, validateLesson])

  const renderManim = useCallback(async () => {
    const parsed = validateLesson()
    if (!parsed) return
    setRendering('manim')
    setRenderResult(null)
    const res = await fetch('/render/manim', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(parsed) })
    const data = await res.json()
    setRenderResult(data)
    setRendering(null)
    if (data.ok) fetchFiles()
  }, [lessonJson, validateLesson])

  const renderAiManim = useCallback(async () => {
    const parsed = validateLesson()
    if (!parsed) return
    if (!groqKey && !window._groqKeyWarned) {
      window._groqKeyWarned = true
      if (!confirm('No Groq API key entered. Set GROQ_API_KEY env var on server or enter a key below.')) return
    }
    setRendering('ai-manim')
    setRenderResult(null)
    const body = { ...parsed, prompt: aiPrompt }
    if (groqKey) body.groq_key = groqKey
    const res = await fetch('/render/ai-manim', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    const data = await res.json()
    setRenderResult(data)
    setRendering(null)
    if (data.ok) fetchFiles()
  }, [lessonJson, validateLesson, aiPrompt, groqKey])

  const outputFiles = fileList?.output || []
  const mediaFiles = fileList?.media || []
  const typstPngs = outputFiles.filter(f => f.name.endsWith('.png'))
  const manimVids = mediaFiles.filter(f => f.name.endsWith('.mp4'))

  return (
    <div className="app">
      <header className="header">
        <h1>Animgen</h1>
        <span className={`health health--${health === 'ok' ? 'ok' : 'err'}`}>
          {health === 'ok' ? 'API connected' : health || 'checking…'}
        </span>
      </header>

      <nav className="tabs">
        {['upload', 'markdown', 'lesson', 'render', 'files'].map(t => (
          <button key={t} className={`tab${tab === t ? ' tab--active' : ''}`} onClick={() => setTab(t)}>
            {t === 'upload' ? 'Upload PDF' : t === 'markdown' ? 'Markdown' : t === 'lesson' ? 'Lesson JSON' : t === 'render' ? 'Render' : 'Files'}
          </button>
        ))}
      </nav>

      {tab === 'upload' && (
        <Section title="Upload PDF">
          <div className="upload-area">
            <input type="file" accept=".pdf" onChange={e => { if (e.target.files[0]) uploadPdf(e.target.files[0]) }} />
            {uploading && <p className="loading">Parsing PDF…</p>}
            {uploadResult && !uploadResult.ok && <p className="error">{uploadResult.error}</p>}
            {uploadResult && uploadResult.ok && (
              <div className="result">
                <p>✅ {uploadResult.filename} → {uploadResult.markdown_file}</p>
              </div>
            )}
          </div>
        </Section>
      )}

      {tab === 'markdown' && (
        <Section title="Markdown Preview">
          <div className="md-controls">
            <select value={selectedMd} onChange={e => loadMarkdown(e.target.value)}>
              <option value="">-- select file --</option>
              {mdFiles.map(f => <option key={f.name} value={f.name}>{f.name}</option>)}
            </select>
            <button onClick={fetchMdFiles}>Refresh</button>
          </div>
          <pre className="md-content">{mdContent || '(no content)'}</pre>
        </Section>
      )}

      {tab === 'lesson' && (
        <Section title="Lesson JSON">
          <p className="hint">Edit the lesson structure below. This feeds both Typst and Manim renders.</p>
          <textarea
            className="json-editor"
            value={lessonJson}
            onChange={e => setLessonJson(e.target.value)}
            spellCheck={false}
          />
          {lessonError && <p className="error">{lessonError}</p>}
          <button onClick={saveLesson}>Save Lesson</button>
        </Section>
      )}

      {tab === 'render' && (
        <Section title="Render">
          <div className="render-actions">
            <button onClick={renderTypst} disabled={rendering !== null}>
              {rendering === 'typst' ? 'Rendering Typst…' : 'Render Typst'}
            </button>
            <button onClick={renderManim} disabled={rendering !== null}>
              {rendering === 'manim' ? 'Rendering Manim…' : 'Render Manim'}
            </button>
            <button className="btn-ai" onClick={renderAiManim} disabled={rendering !== null}>
              {rendering === 'ai-manim' ? 'Generating…' : 'AI Manim'}
            </button>
          </div>

          <details className="ai-options">
            <summary>AI Manim options</summary>
            <div className="ai-options-body">
              <label>Custom prompt (optional):</label>
              <textarea
                className="ai-prompt"
                rows={3}
                value={aiPrompt}
                onChange={e => setAiPrompt(e.target.value)}
                placeholder="e.g. Use a dark background with colorful animated diagrams"
              />
              <label>Groq API key <span className="hint">(leave blank to use server env var)</span>:</label>
              <div className="key-row">
                <input
                  type={showGroqKey ? 'text' : 'password'}
                  className="key-input"
                  value={groqKey}
                  onChange={e => setGroqKey(e.target.value)}
                  placeholder="gsk_..."
                />
                <button className="btn-small" onClick={() => setShowGroqKey(!showGroqKey)}>
                  {showGroqKey ? 'Hide' : 'Show'}
                </button>
              </div>
            </div>
          </details>

          {renderResult && !renderResult.ok && <p className="error">{renderResult.error}</p>}

          {renderResult && renderResult.ok && (
            <div className="render-output">
              <h3>Output Files</h3>
              <ul className="file-list">
                {(renderResult.files || []).map(f => (
                  <li key={f.path || f}>{f.name || f.split('/').pop()}
                    {f.path && <a href={`/${f.path}`} target="_blank" rel="noreferrer"> preview</a>}
                  </li>
                ))}
              </ul>

              {typstPngs.length > 0 && (
                <div className="preview-section">
                  <h3>Typst Preview</h3>
                  {typstPngs.map(f => (
                    <img key={f.name} src={`/output/${f.name}`} alt={f.name} className="preview-img" />
                  ))}
                </div>
              )}

              {manimVids.length > 0 && (
                <div className="preview-section">
                  <h3>Manim Preview</h3>
                  {manimVids.map(f => (
                    <video key={f.name} src={`/media/${f.name}`} controls className="preview-vid" />
                  ))}
                </div>
              )}

              {renderResult.typst_source && (
                <details>
                  <summary>Typst Source</summary>
                  <pre className="code-block">{renderResult.typst_source}</pre>
                </details>
              )}

              {renderResult.scene_source && (
                <details>
                  <summary>AI-Generated Scene ({renderResult.scene_class || '?'})</summary>
                  <pre className="code-block">{renderResult.scene_source}</pre>
                </details>
              )}

              {renderResult.stdout && (
                <details>
                  <summary>Render Log</summary>
                  <pre className="code-block">{renderResult.stdout}</pre>
                </details>
              )}
            </div>
          )}
        </Section>
      )}

      {tab === 'files' && (
        <Section title="Generated Files">
          <button onClick={fetchFiles} style={{ marginBottom: 12 }}>Refresh</button>
          {[
            { label: 'Input PDFs', key: 'input' },
            { label: 'Parsed Markdown', key: 'parsed' },
            { label: 'Output (Typst PNGs, etc.)', key: 'output' },
            { label: 'Media (Manim videos)', key: 'media' },
          ].map(({ label, key }) => (
            <div key={key} className="file-group">
              <h3>{label}</h3>
              {(!fileList || !fileList[key] || fileList[key].length === 0) && <p className="muted">(empty)</p>}
              <ul className="file-list">
                {(fileList?.[key] || []).map(f => (
                  <li key={f.name}>
                    {f.name}
                    <a href={`/${f.path}`} target="_blank" rel="noreferrer"> open</a>
                    <span className="file-size">{f.size} B</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}

          {typstPngs.length > 0 && (
            <div className="preview-section">
              <h3>All Typst PNGs</h3>
              {typstPngs.map(f => (
                <img key={f.name} src={`/output/${f.name}`} alt={f.name} className="preview-img" />
              ))}
            </div>
          )}

          {manimVids.length > 0 && (
            <div className="preview-section">
              <h3>All Manim Videos</h3>
              {manimVids.map(f => (
                <video key={f.name} src={`/media/${f.name}`} controls className="preview-vid" />
              ))}
            </div>
          )}
        </Section>
      )}
    </div>
  )
}

export default App
