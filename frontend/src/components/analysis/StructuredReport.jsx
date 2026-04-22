import React from 'react';
import Plot from 'react-plotly.js';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  BarChart3, 
  Copy,
  ChevronRight
} from 'lucide-react';

const StructuredReport = ({ data }) => {
  if (!data || !data.sections) return null;

  const copyToClipboard = (text) => {
    const fullText = data.sections.map(s => s.content).join('\n\n');
    navigator.clipboard.writeText(fullText);
  };

  // Custom components for ReactMarkdown to ensure premium styling
  const MarkdownComponents = {
    h1: ({node, ...props}) => <h1 style={{ fontFamily: 'Plus Jakarta Sans', fontSize: '2.25rem', fontWeight: 800, marginBottom: '2rem', color: 'white', letterSpacing: '-0.02em' }} {...props} />,
    h2: ({node, ...props}) => <h2 style={{ fontFamily: 'Plus Jakarta Sans', fontSize: '1.4rem', fontWeight: 700, marginTop: '3rem', marginBottom: '1.5rem', color: 'rgba(255,255,255,0.95)', display: 'flex', alignItems: 'center', gap: 14, letterSpacing: '-0.01em' }}>
      <div style={{ width: 4, height: 24, background: '#818cf8', borderRadius: 2 }} /> {props.children}
    </h2>,
    h3: ({node, ...props}) => <h3 style={{ fontFamily: 'Plus Jakarta Sans', fontSize: '1.15rem', fontWeight: 700, marginTop: '2rem', marginBottom: '1rem', color: 'rgba(255,255,255,0.85)' }} {...props} />,
    p: ({node, ...props}) => <p style={{ fontSize: '1.05rem', lineHeight: '1.75', marginBottom: '1.5rem', color: 'rgba(255,255,255,0.85)', fontWeight: 400 }} {...props} />,
    table: ({node, ...props}) => (
      <div style={{ overflowX: 'auto', margin: '2.5rem 0', borderRadius: 16, border: '1px solid rgba(255,255,255,0.08)', background: 'rgba(0,0,0,0.3)', padding: '4px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }} {...props} />
      </div>
    ),
    thead: ({node, ...props}) => <thead style={{ background: 'rgba(255,255,255,0.03)' }} {...props} />,
    th: ({node, ...props}) => <th style={{ padding: '16px 20px', textAlign: 'left', fontWeight: 700, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', fontSize: '0.7rem', letterSpacing: '0.1em' }} {...props} />,
    td: ({node, ...props}) => <td style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255,255,255,0.03)', color: 'rgba(255,255,255,0.7)', lineHeight: '1.5' }} {...props} />,
    li: ({node, ...props}) => <li style={{ marginBottom: '0.75rem', lineHeight: '1.75', color: 'rgba(255,255,255,0.85)' }} {...props} />,
    ul: ({node, ...props}) => <ul style={{ paddingLeft: '1.5rem', marginBottom: '1.5rem' }} {...props} />,
  };

  return (
    <div className="animate-fade-in" style={{ paddingBottom: 100 }}>
      <div 
        style={{ 
          background: 'rgba(26, 28, 35, 0.4)', 
          border: '1px solid rgba(255, 255, 255, 0.05)', 
          borderRadius: 24, 
          padding: 48, 
          backdropFilter: 'blur(20px)',
          position: 'relative'
        }}
      >
        {/* Report Actions */}
        <div style={{ position: 'absolute', top: 32, right: 32, display: 'flex', gap: 12 }}>
          <button 
            onClick={copyToClipboard}
            style={{ 
              background: 'rgba(255,255,255,0.03)', 
              border: '1px solid rgba(255,255,255,0.1)', 
              borderRadius: 8, padding: '8px 12px', color: 'rgba(255,255,255,0.4)',
              fontSize: 10, fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
              transition: 'all 0.2s'
            }}
            className="hover:text-white"
          >
            <Copy size={12} /> COPY DOSSIER
          </button>
        </div>

        {/* Unified Report Content */}
        {data.sections.map((section, idx) => (
          <div key={idx} className="animate-slide-up" style={{ animationDelay: `${idx * 100}ms` }}>
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={MarkdownComponents}
            >
              {section.content}
            </ReactMarkdown>

            {/* Inlined Visualizations */}
            {section.artifact && (
              <div style={{ margin: '2.5rem 0', background: '#0d0e12', borderRadius: 20, padding: 32, border: '1px solid rgba(255,255,255,0.05)', overflow: 'hidden' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
                   <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#818cf8' }} />
                      <span style={{ fontSize: 10, fontWeight: 800, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
                        {section.artifact.title || (section.artifact.type === 'multi_visual' ? 'Tactical Visualizations' : 'Forensic Visualization')}
                      </span>
                   </div>
                </div>

                {section.artifact.type === 'multi_visual' ? (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 40 }}>
                    {section.artifact.data.map((fig, fidx) => (
                      <div key={fidx}>
                        <Plot
                          data={fig.data}
                          layout={{
                            ...fig.layout,
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: { color: '#ffffff', size: 11, family: 'Plus Jakarta Sans' },
                            height: 350,
                            margin: { l: 60, r: 20, t: 30, b: 40 },
                            xaxis: { ...fig.layout?.xaxis, gridcolor: 'rgba(255,255,255,0.05)' },
                            yaxis: { ...fig.layout?.yaxis, gridcolor: 'rgba(255,255,255,0.05)' }
                          }}
                          style={{ width: '100%' }}
                          config={{ displayModeBar: false, responsive: true }}
                        />
                      </div>
                    ))}
                  </div>
                ) : section.artifact.type === 'feature_importance' ? (
                  <Plot
                    data={[{
                      x: Array.isArray(section.artifact.data) ? section.artifact.data.map(i => i.importance) : Object.values(section.artifact.data),
                      y: Array.isArray(section.artifact.data) ? section.artifact.data.map(i => i.feature) : Object.keys(section.artifact.data),
                      type: 'bar',
                      orientation: 'h',
                      marker: { 
                        color: 'rgba(129, 140, 248, 0.6)',
                        line: { color: 'rgba(129, 140, 248, 1)', width: 1 }
                      },
                    }]}
                    layout={{
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#ffffff', size: 10, family: 'Plus Jakarta Sans' },
                      margin: { l: 150, r: 20, t: 10, b: 40 },
                      height: 400,
                      xaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false },
                      yaxis: { gridcolor: 'rgba(255,255,255,0.05)', zeroline: false, autorange: 'reversed' }
                    }}
                    style={{ width: '100%' }}
                    config={{ displayModeBar: false, responsive: true }}
                  />
                ) : section.artifact.type === 'confusion_matrix' ? (
                  <Plot
                    data={[{
                      z: section.artifact.data,
                      type: 'heatmap',
                      colorscale: 'Viridis',
                      showscale: true,
                    }]}
                    layout={{
                      paper_bgcolor: 'rgba(0,0,0,0)',
                      plot_bgcolor: 'rgba(0,0,0,0)',
                      font: { color: '#ffffff', size: 10, family: 'Plus Jakarta Sans' },
                      margin: { l: 40, r: 40, t: 10, b: 40 },
                      height: 350,
                      xaxis: { title: 'Predicted', gridcolor: 'rgba(255,255,255,0.05)' },
                      yaxis: { title: 'Actual', gridcolor: 'rgba(255,255,255,0.05)' }
                    }}
                    style={{ width: '100%' }}
                    config={{ displayModeBar: false, responsive: true }}
                  />
                ) : section.type === 'visualization' ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 60, opacity: 0.1 }}>
                    <BarChart3 size={48} />
                    <p style={{ fontSize: 12, marginTop: 16 }}>Synthesizing graphical trace...</p>
                  </div>
                ) : null}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default StructuredReport;
