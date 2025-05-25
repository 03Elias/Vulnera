// src/components/Submitpage.jsx
import { useState, useEffect, useRef } from 'react'
import JSZip from 'jszip'
import submitImage from '../assets/submit.png'

// Read your env
const rawApiUrl = import.meta.env.VITE_API_URL
const API_URL = (rawApiUrl || window.location.origin).replace(/\/$/, '')

async function getFilesFromDir(dirHandle, root = '') {
  let files = []
  for await (let [name, handle] of dirHandle.entries()) {
    if (handle.kind === 'file') {
      const file = await handle.getFile()
      Object.defineProperty(file, 'webkitRelativePath', {
        value: root + name,
        writable: false,
      })
      files.push(file)
    } else if (handle.kind === 'directory') {
      files = files.concat(
        await getFilesFromDir(handle, `${root}${name}/`)
      )
    }
  }
  return files
}

export default function Submitpage() {
  const [showChoice, setShowChoice] = useState(false)
  const [isUploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  // ref to the results container
  const resultsRef = useRef(null)

  // Animate a ~20s progress bar
  useEffect(() => {
    if (!isUploading) return
    setProgress(0)
    const start = Date.now()
    const timer = setInterval(() => {
      const p = Math.min(100, ((Date.now() - start) / 20000) * 100)
      setProgress(p)
      if (p >= 100) clearInterval(timer)
    }, 100)
    return () => clearInterval(timer)
  }, [isUploading])

  // Auto-scroll to results when done
  useEffect(() => {
    if (result && !isUploading && resultsRef.current) {
      // give a brief delay so CSS transition finishes
      setTimeout(() => {
        resultsRef.current.scrollIntoView({ behavior: 'smooth' })
      }, 300)
    }
  }, [result, isUploading])

  const handleImageClick = () => {
    setError(null)
    setResult(null)
    setShowChoice(true)
  }

  const handleUpload = async (isFolder) => {
    setError(null)
    setResult(null)
    setShowChoice(false)

    let files = []
    try {
      if (isFolder && window.showDirectoryPicker) {
        const dirHandle = await window.showDirectoryPicker()
        files = await getFilesFromDir(dirHandle)
      } else if (window.showOpenFilePicker) {
        const handles = await window.showOpenFilePicker({ multiple: true })
        files = await Promise.all(handles.map(h => h.getFile()))
      } else {
        files = await new Promise(res => {
          const inp = document.createElement('input')
          inp.type = 'file'
          inp.multiple = true
          inp.onchange = () => res(Array.from(inp.files))
          inp.click()
        })
      }
    } catch {
      setError('Selection cancelled or not supported')
      return
    }

    if (!files.length) {
      setError('No files selected')
      return
    }

    setUploading(true)
    try {
      const zip = new JSZip()
      files.forEach(f => {
        const p = f.webkitRelativePath || f.name
        zip.file(p, f)
      })
      const blob = await zip.generateAsync({ type: 'blob' })

      const fd = new FormData()
      fd.append('file', blob, 'upload.zip')
      const res = await fetch(`${API_URL}/analyze-upload/`, {
        method: 'POST',
        body: fd,
      })
      if (!res.ok) throw new Error(`Server ${res.status}`)
      const json = await res.json()

      // ensure at least 15s
      await new Promise(r => setTimeout(r, 15000))
      setResult(json)
    } catch (err) {
      console.error(err)
      setError(err.message)
    } finally {
      setUploading(false)
    }
  }

  const isFolderRes = Array.isArray(result) && result.some(x => x.overall_analysis)
  const overall = isFolderRes && result.find(x => x.overall_analysis).overall_analysis
  const files = Array.isArray(result) ? result.filter(x => !x.overall_analysis) : []

  const containerClass = [
    'submit-body-container',
    isUploading ? 'progressing' : '',
  ].join(' ')
  const progressClass = [
    'progress-container',
    (!isUploading && result) ? 'complete' : '',
  ].join(' ')

  return (
    <div className={containerClass}>
      <div className="instruction-container">
        <h1>Upload Your Code Folder or File for Analysis</h1>
        <p>We analyze your submission for potential threats, but your code stays private, and no findings are saved.</p>
      </div>

      <div className="submit-image-container">
        {!showChoice ? (
          <img
            src={submitImage}
            alt="Submit"
            className="submit-image"
            onClick={handleImageClick}
          />
        ) : (
          <div className="choice-buttons">
            <button onClick={() => handleUpload(true)}>Upload Folder</button>
            <button onClick={() => handleUpload(false)}>Upload File(s)</button>
          </div>
        )}
      </div>

      {isUploading && (
        <div className={progressClass}>
          <div className="progress-bar-container">
            <div
              className="progress-bar"
              style={{ transform: `scaleX(${progress / 100})` }}
            />
          </div>
          <p className="analyzing-progress">Analyzing… please wait</p>
        </div>
      )}

      {error && <p className="error">Error: {error}</p>}

      {/* resultsRef attaches here */}
      {result && (
        <div className="analysis-results" ref={resultsRef}>
          {isFolderRes ? (
            <>
              <section className="overall-analysis">
                <h2>Project Risk: {overall.overall_danger.toUpperCase()}</h2>
                <p>{overall.overall_reason}</p>
              </section>
              <section className="file-list">
                <h3>File‐by‐file Analysis</h3>
                {files.map((file, i) => (
                  <details key={i} className="file-detail">
                    <summary>
                      {file.filename} — Risk: {file.danger.toUpperCase()}
                    </summary>
                    <pre className="code-block">{file.code}</pre>
                    <p><strong>Reason:</strong> {file.reason}</p>
                  </details>
                ))}
              </section>
            </>
          ) : (
            <section className="file-analysis">
              <h2>Risk: {result[0].danger.toUpperCase()}</h2>
              <pre className="code-block">{result[0].code}</pre>
              <p><strong>Reason:</strong> {result[0].reason}</p>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
