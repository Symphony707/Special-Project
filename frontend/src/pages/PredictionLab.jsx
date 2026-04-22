import { useState, useEffect, useCallback } from 'react'
import { useNavigate }     from 'react-router-dom'
import useStore            from '../store/useStore'
import ChatPanel           from '../components/chat/ChatPanel'
import StructuredReport    from '../components/analysis/StructuredReport'
import { suggestTarget, runPrediction }
                           from '../api/prediction'
import toast               from 'react-hot-toast'

export default function PredictionLab() {
  const navigate = useNavigate()
  const activeFile        = useStore(s => s.activeFile)
  const predictionResults = useStore(s => s.predictionResults || [])
  const addPredictionResult = useStore(s => s.addPredictionResult)
  const setSuggestedTarget  = useStore(s => s.setSuggestedTarget)
  const storedSuggestion    = useStore(s => s.suggestedTarget)

  const [targetCol,  setTargetCol]  = useState('')
  const [taskType,   setTaskType]   = useState('regression')
  const [useRF,      setUseRF]      = useState(true)
  const [useGB,      setUseGB]      = useState(true)
  const [useLR,      setUseLR]      = useState(true)
  const [running,    setRunning]    = useState(false)
  const [runStep,    setRunStep]    = useState(0)
  const [loadingSuggestion, setLoadingSuggestion] = useState(false)
  const [suggestion, setSuggestion] = useState(null)

  const columns = suggestion?.columns || 
                 (activeFile?.fingerprint?.columns ? Object.keys(activeFile.fingerprint.columns) : [])
  const latestResult = predictionResults[0] || null

  // Load suggestion on mount
  useEffect(() => {
    if (!activeFile?.id) return
    setLoadingSuggestion(true)
    suggestTarget(activeFile.id)
      .then(res => {
        const data = res
        setSuggestion(data)
        setSuggestedTarget(data.suggested_target, data.task_type)
        if (data?.suggested_target && !targetCol) {
          setTargetCol(data.suggested_target)
          setTaskType(data.task_type || 'regression')
        }
      })
      .catch(() => {
        // Silently fail — user can still select manually
      })
      .finally(() => setLoadingSuggestion(false))
  }, [activeFile?.id])

  // Update task type when column changes
  useEffect(() => {
    if (!targetCol) return
    
    // If it's a known suggestion, use that type
    if (suggestion?.all_candidates?.includes(targetCol)) {
      setTaskType(suggestion.task_type || 'regression')
      return
    }
    
    // Otherwise detect from fingerprint
    const colMeta = activeFile?.fingerprint?.columns?.[targetCol]
    if (colMeta) {
      if (colMeta.dtype === 'categorical' || colMeta.unique_count <= 15) {
        setTaskType('classification')
      } else {
        setTaskType('regression')
      }
    }
  }, [targetCol, suggestion, activeFile])

  const handleRun = useCallback(async () => {
    if (!activeFile?.id) {
      toast.error('No dataset active')
      return
    }

    setRunning(true)
    setRunStep(1)

    // Animate steps for visual feedback
    const t2 = setTimeout(() => setRunStep(2), 2000)
    const t3 = setTimeout(() => setRunStep(3), 5000)

    try {
      const res = await runPrediction({
        file_id:       activeFile.id,
        target_column: targetCol,
        models:        ['RandomForest', 'GradientBoosting', 'LinearModel'],
      })
      addPredictionResult(res.structured_response)
      toast.success('Prediction complete!')
    } catch (err) {
      const detail = err.response?.data?.detail
      if (typeof detail === 'object' && detail?.blockers) {
        toast.error(detail.blockers[0] || 'Prediction failed')
      } else {
        toast.error(
          typeof detail === 'string'
            ? detail
            : 'Prediction failed. Check your target column.')
      }
    } finally {
      clearTimeout(t2); clearTimeout(t3)
      setRunning(false)
      setRunStep(0)
    }
  }, [targetCol, activeFile, useRF, useGB, useLR,
      addPredictionResult])

  // No file loaded
  if (!activeFile) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center',
        justifyContent: 'center',
        height: 'calc(100vh - 110px)',
        flexDirection: 'column', gap: 16,
        color: '#8899bb', fontFamily: 'DM Sans, sans-serif'
      }}>
        <div style={{ fontSize: 56, opacity: 0.3 }}>🔮</div>
        <div style={{
          fontFamily: 'Syne, sans-serif', fontSize: 20,
          fontWeight: 700, color: '#eef2ff'
        }}>No Dataset Loaded</div>
        <div style={{ fontSize: 13, color: '#4a5a7a' }}>
          Load a dataset from the Data Manager to begin
        </div>
        <button
          onClick={() => navigate('/data')}
          style={{
            marginTop: 8, padding: '10px 24px',
            borderRadius: 10,
            background: 'linear-gradient(135deg,#06d2ff,#0499cc)',
            color: '#08111f', fontWeight: 700,
            fontSize: 13, border: 'none', cursor: 'pointer'
          }}
        >
          Go to Data Manager
        </button>
      </div>
    )
  }

  // Render full 3-column layout
  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '260px 1fr 320px',
      gap: 16,
      height: `calc(100vh - 140px)`,
      overflow: 'hidden',
    }}>

      {/* LEFT: Setup Panel */}
      <LeftSetupPanel
        columns={columns}
        targetCol={targetCol}
        setTargetCol={setTargetCol}
        taskType={taskType}
        suggestion={suggestion}
        loadingSuggestion={loadingSuggestion}
        useRF={useRF} setUseRF={setUseRF}
        useGB={useGB} setUseGB={setUseGB}
        useLR={useLR} setUseLR={setUseLR}
        running={running}
        runStep={runStep}
        onRun={handleRun}
        latestResult={latestResult}
      />

      {/* CENTER: Results */}
      <CenterResults
        running={running}
        runStep={runStep}
        result={latestResult}
        allResults={predictionResults}
        addResult={addPredictionResult}
      />

      {/* RIGHT: Chat */}
      <ChatPanel
        title="Prediction AI"
        accentColor="var(--purple)"
        dotColor="#7c6fff"
        fileId={activeFile.id}
        placeholder="Ask about model results..."
        suggestions={[
          'What would improve my model accuracy?',
          'Which features are most important?',
          'How reliable are these predictions?',
          'What does the confusion matrix mean?',
        ]}
      />
    </div>
  )
}

// ── Sub-components defined in same file ──

function LeftSetupPanel({
  columns, targetCol, setTargetCol, taskType,
  suggestion, loadingSuggestion, useRF, setUseRF, useGB, setUseGB,
  useLR, setUseLR, running, runStep, onRun, latestResult
}) {
  const taskColors = {
    classification: { bg:'rgba(124,111,255,0.12)',
                      color:'#7c6fff',
                      border:'rgba(124,111,255,0.25)' },
    regression:     { bg:'rgba(6,210,255,0.10)',
                      color:'#06d2ff',
                      border:'rgba(6,210,255,0.25)' },
    timeseries:     { bg:'rgba(255,181,71,0.10)',
                      color:'#ffb547',
                      border:'rgba(255,181,71,0.25)' },
  }
  const tc = taskColors[taskType] || taskColors.regression

  const steps = [
    'Preprocessing data...',
    'Training models...',
    'Evaluating results...',
  ]

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 14,
      padding: 18,
      overflowY: 'auto',
      display: 'flex',
      flexDirection: 'column',
      gap: 20,
    }}>
      {/* Simulation Engine Status */}
      <div style={{
        background: 'rgba(6,210,255,0.03)',
        border: '1px solid rgba(6,210,255,0.1)',
        borderRadius: 12,
        padding: 16,
        display: 'flex',
        flexDirection: 'column',
        gap: 12,
      }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
        }}>
           <div style={{
             width: 10, height: 10, borderRadius: '50%',
             background: '#7c6fff',
             boxShadow: '0 0 10px #7c6fff'
           }} className={running ? "pulse-dot" : ""} />
           <div style={{ fontSize: 13, color: '#eef2ff', fontWeight: 600 }}>
             Neural Optimization Active
           </div>
        </div>
        <div style={{ fontSize: 11, color: '#6a7a9a', lineHeight: 1.5 }}>
          The forensic engine is monitoring the workspace and is ready to execute a multi-architecture trajectory simulation.
        </div>
      </div>

      <div style={{
        height: 1, background: 'var(--border-subtle)'
      }} />

      <div style={{
        height: 1, background: 'var(--border-subtle)',
        margin: '8px 0'
      }} />

      {/* Main Action */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        <button
          onClick={onRun}
          disabled={running}
          style={{
            width: '100%',
            height: 48,
            borderRadius: 10,
            background: running 
              ? 'rgba(255,255,255,0.05)'
              : 'linear-gradient(135deg, #06d2ff, #0499cc)',
            color: running ? '#4a5a7a' : '#08111f',
            fontWeight: 800,
            fontSize: 13,
            border: 'none',
            cursor: running ? 'not-allowed' : 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            gap: 10,
            transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
            boxShadow: running ? 'none' : '0 4px 15px rgba(6,210,255,0.2)'
          }}
        >
          {running ? (
            <>
              <div style={{
                width: 14, height: 14,
                border: '2px solid rgba(6,210,255,0.2)',
                borderTopColor: '#06d2ff',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }} />
              <span>Simulating...</span>
            </>
          ) : (
            <>
              <span>Run Autonomous Simulation →</span>
            </>
          )}
        </button>

        {/* Stats Summary */}
        {latestResult && !running && (
          <div style={{
            padding: '12px 14px',
            background: 'rgba(255,255,255,0.03)',
            borderRadius: 10,
            border: '1px solid var(--border-subtle)',
          }}>
             <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: 4 }}>Last Success</div>
             <div style={{ fontSize: 13, color: '#eef2ff', fontWeight: 600 }}>
               {latestResult.best_model} — {(latestResult.accuracy * 100).toFixed(1)}%
             </div>
          </div>
        )}
      </div>

      {/* Real-time Telemetry */}
      {running && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <div style={{ fontSize: 10, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Neural Telemetry</div>
          {steps.map((step, i) => {
            const done    = runStep > i + 1
            const active  = runStep === i + 1
            const pending = runStep < i + 1
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'center',
                gap: 8,
                opacity: pending ? 0.35 : 1,
                transition: 'opacity 0.4s ease',
              }}>
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: done ? 'var(--green)' : active ? 'var(--cyan)' : 'var(--text-muted)',
                  boxShadow: active ? '0 0 6px var(--cyan)' : 'none',
                  animation: active ? 'pulse 1s infinite' : 'none',
                  flexShrink: 0,
                }} />
                <span style={{
                  fontSize: 12,
                  color: done ? 'var(--green)' : active ? 'var(--cyan)' : 'var(--text-muted)',
                  fontWeight: active ? 600 : 400
                }}>
                  {step}
                </span>
              </div>
            )
          })}
        </div>
      )}
      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0%,100%{opacity:1} 50%{opacity:0.4}
        }
      `}</style>
    </div>
  )
}

function CenterResults({ running, runStep, result, allResults }) {
  const steps = [
    'Preprocessing data...',
    'Training models...',
    'Evaluating results...',
  ]

  if (running) {
    return (
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 14,
        display: 'flex', alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column', gap: 20,
      }}>
        {/* Animated rings */}
        <div style={{ position: 'relative', width: 80, height: 80 }}>
          {[0,1,2].map(i => (
            <div key={i} style={{
              position: 'absolute', inset: i * 10,
              border: '1.5px solid rgba(6,210,255,0.2)',
              borderTop: '1.5px solid var(--cyan)',
              borderRadius: '50%',
              animation: `spin ${0.8 + i * 0.4}s linear infinite`,
            }} />
          ))}
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center',
            justifyContent: 'center',
            fontSize: 24,
          }}>🔮</div>
        </div>
        <div style={{
          fontFamily: 'Syne, sans-serif', fontSize: 24,
          fontWeight: 700, color: 'var(--text-primary)',
          letterSpacing: '-0.02em'
        }}>Neural Training Cycle Active</div>
        <div style={{ display: 'flex', flexDirection: 'column',
                      gap: 12, alignItems: 'center' }}>
          {steps.map((step, i) => {
            const isActive = runStep === i + 1;
            const isDone = runStep > i + 1;
            return (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 12,
                fontSize: 13,
                color: isDone ? 'var(--green)'
                      : isActive ? 'var(--cyan)'
                      : 'var(--text-muted)',
                opacity: (isActive || isDone) ? 1 : 0.4,
                transition: 'all 0.4s',
                fontFamily: 'DM Sans, sans-serif'
              }}>
                <div style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: isDone ? 'var(--green)' : isActive ? 'var(--cyan)' : 'transparent',
                  border: isDone || isActive ? 'none' : '1px solid var(--text-muted)',
                  boxShadow: isActive ? '0 0 10px var(--cyan)' : 'none'
                }} />
                {step}
              </div>
            );
          })}
        </div>
        <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      </div>
    )
  }

  if (!result) {
    return (
      <div style={{
        flex: 1,
        background: 'rgba(13, 14, 18, 0.4)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 24,
        display: 'flex', alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column', gap: 20,
        backdropFilter: 'blur(10px)',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Grid/Pattern */}
        <div style={{
          position: 'absolute', inset: 0,
          backgroundImage: 'radial-gradient(circle at 2px 2px, rgba(255,255,255,0.03) 1px, transparent 0)',
          backgroundSize: '24px 24px',
          zIndex: 0
        }} />

        <div style={{
          fontSize: 80, opacity: 0.15,
          filter: 'drop-shadow(0 0 20px var(--cyan))',
          animation: 'pulseSimulation 4s ease-in-out infinite',
          zIndex: 1
        }}>🔭</div>
        
        <div style={{
          fontFamily: 'Syne, sans-serif', fontSize: 20,
          fontWeight: 800, color: 'var(--text-primary)',
          letterSpacing: '0.05em', textTransform: 'uppercase',
          zIndex: 1
        }}>Forensic Lab Ready</div>
        
        <div style={{
          fontSize: 13, color: 'var(--text-muted)',
          maxWidth: 320, textAlign: 'center', lineHeight: 1.8,
          zIndex: 1, fontWeight: 500
        }}>
          Awaiting target synchronization. Select a dimension from the workspace to initiate a neural trajectory simulation.
        </div>

        <style>{`
          @keyframes pulseSimulation {
            0%, 100% { transform: scale(1); opacity: 0.15; }
            50% { transform: scale(1.05); opacity: 0.25; }
          }
        `}</style>
      </div>
    )
  }

  // Has results — render structured report
  const sr = result // result IS the structured response
 
  // Model comparison cards
  const cvTable   = sr.cv_scores_table || []
  const bestModel = sr.best_model || 'Neural Engine'
  const accuracy  = sr.accuracy ?? 0

  return (
    <div style={{
      overflowY: 'auto',
      display: 'flex', flexDirection: 'column', gap: 14,
      padding: '2px 0',
    }}>
      {/* Model comparison row */}
      {cvTable.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: `repeat(${Math.min(cvTable.length,3)}, 1fr)`,
          gap: 12,
        }}>
          {cvTable.slice(0,3).map((m, i) => {
            const mName    = m.Model || m.model || `Model ${i+1}`
            const isWinner = mName === bestModel
            const rawScore = m['Mean Accuracy'] || m['Mean R2'] || m.cv_score || 0
            const score    = typeof rawScore === 'string' ? parseFloat(rawScore) : rawScore
            
            return (
              <div key={i} style={{
                background: isWinner
                  ? 'rgba(0,224,150,0.05)'
                  : 'var(--bg-elevated)',
                border: `1px solid ${isWinner
                  ? 'rgba(0,224,150,0.35)'
                  : 'var(--border-subtle)'}`,
                borderRadius: 12, padding: '14px 16px',
                position: 'relative',
                animation: isWinner
                  ? 'winnerPulse 2s ease infinite'
                  : 'none',
              }}>
                {isWinner && (
                  <div style={{
                    position: 'absolute', top: 8, right: 10,
                    fontSize: 9, fontWeight: 700,
                    color: 'var(--green)',
                    letterSpacing: '0.08em',
                  }}>✦ BEST</div>
                )}
                <div style={{
                  fontSize: 12, fontWeight: 600,
                  color: 'var(--text-secondary)',
                  marginBottom: 6,
                }}>{mName}</div>
                <div style={{
                  fontFamily: 'Syne, sans-serif',
                  fontSize: 24, fontWeight: 800,
                  color: isWinner
                    ? 'var(--green)'
                    : 'var(--text-primary)',
                }}>
                  {(score * 100).toFixed(1)}%
                </div>
                <div style={{
                  fontSize: 10, color: 'var(--text-muted)',
                  marginBottom: 8,
                }}>CV Accuracy</div>
                <div style={{
                  height: 4, background: 'var(--border-subtle)',
                  borderRadius: 2, overflow: 'hidden',
                }}>
                  <div style={{
                    width: `${score * 100}%`, height: '100%',
                    background: isWinner
                      ? 'var(--green)' : 'var(--cyan)',
                    borderRadius: 2,
                    transition: 'width 0.8s ease',
                  }} />
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Structured sections */}
      {sr.sections?.length > 0 && (
        <StructuredReport
          data={sr}
        />
      )}

      {/* Fallback if no sections */}
      {(!sr.sections || sr.sections.length === 0) && (
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 14, padding: 24,
        }}>
          <div style={{
            fontSize: 14, color: 'var(--text-primary)',
            lineHeight: 1.7,
          }}>
            <strong>Best model: {bestModel}</strong><br />
            Accuracy: {(accuracy * 100).toFixed(1)}%
          </div>
        </div>
      )}

      <style>{`
        @keyframes winnerPulse {
          0%,100%{box-shadow:0 0 0 0 rgba(0,224,150,0)}
          50%{box-shadow:0 0 0 4px rgba(0,224,150,0.15)}
        }
      `}</style>
    </div>
  )
}
