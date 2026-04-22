import React, { useState, useEffect } from 'react';
import { 
  FlaskConical, 
  Database, 
  ShieldAlert, 
  ChevronRight, 
  Sparkles,
  History,
  FileText,
  PlayCircle
} from 'lucide-react';
import toast from 'react-hot-toast';

import useStore from '../store/useStore';
import { runAnalysis, getAnalysis } from '../api/analysis';
import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import SectionHeader from '../components/ui/SectionHeader';
import EmptyState from '../components/ui/EmptyState';
import StructuredReport from '../components/analysis/StructuredReport';
import ChatPanel from '../components/chat/ChatPanel';

export default function AnalysisLab() {
  const { 
    activeFile, analysisResults, addAnalysisResult, 
    dashboardAnalysis, setDashboardAnalysis 
  } = useStore();
  
  const [isRunning, setIsRunning] = useState(false);
  const [query, setQuery] = useState("");
  const [selectedResultIndex, setSelectedResultIndex] = useState(0);

  // Sync dashboard analysis if it exists
  useEffect(() => {
    if (dashboardAnalysis) {
      // It's already in the store, just clear the dashboard trigger
      setDashboardAnalysis(null);
    }
  }, [dashboardAnalysis]);

  const handleRunAnalysis = async () => {
    if (!activeFile || !query.trim() || isRunning) return;

    setIsRunning(true);
    const tid = toast.loading("Deploying Analytical Agents...");
    try {
      const res = await runAnalysis({
        file_id: activeFile.id,
        query: query
      });
      addAnalysisResult(res.structured_response);
      setSelectedResultIndex(0);
      setQuery("");
      toast.success("Analysis Complete", { id: tid });
    } catch (err) {
      toast.error("Agent failed to synthesize findings", { id: tid });
    } finally {
      setIsRunning(false);
    }
  };

  if (!activeFile) {
    return (
      <div className="h-full flex items-center justify-center animate-fade-in">
        <EmptyState 
          icon={<FlaskConical size={48} className="text-white/10" />} 
          title="Laboratory Offline" 
          subtitle="Initialize an asset from the Dashboard to begin forensic investigation." 
        />
      </div>
    );
  }

  const currentResult = analysisResults[selectedResultIndex];

  return (
    <div className="animate-fade-in" style={{ 
      display: 'grid', 
      gridTemplateColumns: '300px 1fr 360px', 
      gap: 24, 
      height: 'calc(100vh - 140px)' 
    }}>
      {/* Column 1: Control Panel */}
      <div className="scrollbar-hide" style={{ flex: 'none', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        <Card className="glass" style={{ padding: 20, borderColor: 'rgba(255,255,255,0.1)' }}>
          <SectionHeader label="Active Intelligence" />
          <div style={{ marginTop: 16, display: 'flex', alignItems: 'start', gap: 12 }}>
            <div style={{ padding: 8, borderRadius: 8, background: 'rgba(99, 102, 241, 0.1)', color: '#818cf8' }}>
              <Database size={18} />
            </div>
            <div style={{ flex: 1, overflow: 'hidden' }}>
              <h3 style={{ fontSize: 14, fontWeight: 700, color: 'rgba(255,255,255,0.9)' }} className="truncate">{activeFile.name}</h3>
              <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '0.1em', marginTop: 4 }}>
                {activeFile.rowCount?.toLocaleString()} Vectors Detected
              </p>
            </div>
          </div>
          
          <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, textTransform: 'uppercase', color: 'rgba(255,255,255,0.4)', marginBottom: 6 }}>
                <span>Signal Integrity</span>
                <span style={{ color: '#10b981' }}>High</span>
              </div>
              <div style={{ height: 4, background: 'rgba(255,255,255,0.05)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{ height: '100%', width: '94%', background: 'rgba(16, 185, 129, 0.5)' }} />
              </div>
            </div>
            
            {activeFile.fingerprint?.pii_detected && (
              <div style={{ padding: 12, borderRadius: 8, background: 'rgba(245, 158, 11, 0.05)', border: '1px solid rgba(245, 158, 11, 0.2)', display: 'flex', gap: 12 }}>
                <ShieldAlert size={14} style={{ color: '#f59e0b', flexShrink: 0, marginTop: 2 }} />
                <p style={{ fontSize: 10, color: 'rgba(254, 243, 199, 0.6)', lineHeight: 1.5 }}>
                  PII Patterns detected. Neural masking protocols active.
                </p>
              </div>
            )}
          </div>
        </Card>

        <Card className="glass" style={{ padding: 20, borderColor: 'rgba(255,255,255,0.1)' }}>
          <SectionHeader label="Start New Study" />
          <div style={{ marginTop: 16, position: 'relative' }}>
            <textarea 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Describe your investigation intent..."
              style={{
                width: '100%', background: 'rgba(0,0,0,0.4)', border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: 12, padding: '12px 16px', fontSize: 12, color: 'white',
                outline: 'none', resize: 'none', height: 128, transition: 'all 0.2s'
              }}
            />
            <Button 
              onClick={handleRunAnalysis}
              disabled={!query.trim() || isRunning}
              variant="intelligence" 
              fullWidth 
              style={{ marginTop: 12 }}
            >
              {isRunning ? <Sparkles className="animate-spin" size={14} style={{ marginRight: 8 }}/> : <PlayCircle size={14} style={{ marginRight: 8 }}/>}
              Run Forensic Pulse
            </Button>
          </div>
        </Card>

        {analysisResults.length > 0 && (
          <div style={{ marginTop: 8 }}>
            <SectionHeader label="Previous Dossiers" />
            <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 8 }}>
              {analysisResults.map((res, i) => (
                <div 
                  key={i}
                  onClick={() => setSelectedResultIndex(i)}
                  style={{ 
                    display: 'flex', alignItems: 'center', gap: 12, padding: 12, 
                    borderRadius: 12, border: '1px solid', cursor: 'pointer', transition: 'all 0.2s',
                    background: selectedResultIndex === i ? 'rgba(255,255,255,0.1)' : 'transparent',
                    borderColor: selectedResultIndex === i ? 'rgba(255,255,255,0.2)' : 'transparent'
                  }}
                >
                  <FileText size={14} style={{ color: selectedResultIndex === i ? '#818cf8' : 'rgba(255,255,255,0.2)' }} />
                  <div style={{ flex: 1, overflow: 'hidden' }}>
                    <p style={{ fontSize: 11, fontWeight: 600, color: selectedResultIndex === i ? 'white' : 'var(--text-secondary)' }} className="truncate">
                      {res.sections[0]?.content.substring(0, 40)}...
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Column 2: Center Stage */}
      <div className="scrollbar-hide" style={{ overflowY: 'auto', padding: '0 16px' }}>
        {currentResult ? (
          <StructuredReport data={currentResult} />
        ) : (
          <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: 0.2, textAlign: 'center' }}>
            <div className="animate-pulse justify-center" style={{ width: 64, height: 64, borderRadius: '50%', border: '2px dashed rgba(255,255,255,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24 }}>
              <Sparkles size={24} />
            </div>
            <h2 className="syne" style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 8 }}>Awaiting Intelligence</h2>
            <p style={{ fontSize: 13, maxWidth: '320px' }}>Run a forensic pulse or ask the chat to generate analytical reports.</p>
          </div>
        )}
      </div>

      {/* Column 3: Chat Panel */}
      <div style={{ height: '100%' }}>
        <ChatPanel 
          title="Analysis AI"
          accentColor="var(--cyan)"
          dotColor="#06d2ff"
          fileId={activeFile.id}
          placeholder="Ask about your findings..."
          suggestions={[
            'Identify data outliers',
            'Draft findings summary',
            'Scan dossier segments',
            'Explain statistical variance',
          ]}
        />
      </div>
    </div>
  );
}
