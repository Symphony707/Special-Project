import React, { useState, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';
import { 
  CloudUpload, 
  Database, 
  Microscope, 
  Cpu, 
  ChevronRight, 
  Sparkles,
  Search,
  Settings,
  History,
  Trash2,
  FileText,
  TrendingUp,
  Brain
} from 'lucide-react';

import useStore from '../store/useStore';
import { uploadFile, listFiles, loadFile } from '../api/files';
import { getStats, getActivity, initializeAsset, getOllamaStatus } from '../api/dashboard';
import { quickSummary } from '../api/analysis';
import { suggestTarget, autoPredict } from '../api/prediction';

import Card from '../components/ui/Card';
import Badge from '../components/ui/Badge';
import Button from '../components/ui/Button';
import KPICard from '../components/ui/KPICard';
import SectionHeader from '../components/ui/SectionHeader';
import EmptyState from '../components/ui/EmptyState';

export default function Dashboard() {
  const navigate = useNavigate();
  const { 
    activeFile, setActiveFile, user, userFiles, setUserFiles, 
    dashStats, setDashStats, dashActivity, setDashActivity,
    setDashboardAnalysis, setDashboardPrediction, 
    setSuggestedTarget, suggestedTarget, 
    addAnalysisResult, addPredictionResult
  } = useStore();

  
  const [isUploading, setIsUploading] = useState(false);
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [predRunning, setPredRunning] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState({ status: 'checking', model: null });

  useEffect(() => {
    refreshData();
    checkOllama();
    const timer = setInterval(checkOllama, 30000);
    return () => clearInterval(timer);
  }, []);

  const checkOllama = async () => {
    try {
        const res = await getOllamaStatus();
        setOllamaStatus(res.data);
    } catch (err) {
        setOllamaStatus({ status: 'offline', model: null });
    }
  };

  useEffect(() => {
    if (activeFile) {
        refreshActivity();
    }
  }, [activeFile]);

  const refreshData = async () => {
    try {
        const [filesRes, statsRes] = await Promise.all([
            listFiles(),
            getStats()
        ]);
        setUserFiles(filesRes.data.files);
        setDashStats(statsRes.data);
    } catch (err) {
        console.error('Failed to load dashboard data', err);
    }
  };

  const refreshActivity = async () => {
    if (!activeFile) return;
    try {
        const res = await getActivity(activeFile.id);
        setDashActivity({
            patterns: res.data?.patterns || [],
            activity: res.data?.activity || []
        });
    } catch (err) {
        console.error('Failed to load activity', err);
        setDashActivity({ patterns: [], activity: [] });
    }
  };

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    
    if (user?.is_guest && userFiles.length >= 1) {
        toast.error('Restricted: Guests can only upload one asset. Please register.');
        return;
    }

    setIsUploading(true);
    const tid = toast.loading(`Ingesting ${file.name}...`);
    try {
        const res = await uploadFile(file);
        toast.success('Asset secured in vault', { id: tid });
        
        await initializeAsset(res.data.file_id);
        setActiveFile(res.data.file_id, file.name, {
            rowCount: res.data.row_count,
            colCount: res.data.col_count,
            fingerprint: res.data.fingerprint
        });
        refreshData();
    } catch (err) {
        toast.error(err.response?.data?.detail || 'Ingestion failed', { id: tid });
    } finally {
        setIsUploading(false);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop, 
    multiple: false,
    accept: { 
        'text/csv': ['.csv'], 
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
        'application/json': ['.json']
    }
  });

  const handleLoad = async (id, name) => {
    const tid = toast.loading(`Activating ${name}...`);
    try {
        const res = await loadFile(id);
        setActiveFile(id, name, {
            rowCount: res.data.row_count,
            colCount: res.data.col_count,
            fingerprint: res.data.fingerprint
        });
        toast.success(`Active Asset: ${name}`, { id: tid });
    } catch (err) {
        toast.error('Failed to load artifact', { id: tid });
    }
  };

  const handleQuickSummary = async () => {
    if (!activeFile?.id || analysisRunning) return;
    
    setAnalysisRunning(true);
    const tid = toast.loading("Deploying Analytical Agents...");
    
    try {
      const res = await quickSummary(activeFile.id);
      addAnalysisResult(res.structured_response);
      setDashboardAnalysis(res.structured_response);
      
      toast.success("Dossier Synthesized", { id: tid });
      // Smooth transition to Lab
      setTimeout(() => navigate('/analysis'), 800);
    } catch (err) {
      toast.error("Agent communication failed", { id: tid });
      // Still navigate to allow manual retry
      setTimeout(() => navigate('/analysis'), 1000);
    } finally {
      setAnalysisRunning(false);
    }
  };

  const handleAutoPredict = async () => {
    if (!activeFile?.id || predRunning) return;

    setPredRunning(true);
    const tid = toast.loading("Launching Prediction Engine...");

    try {
      let targetColumn = suggestedTarget?.target;
      
      if (!targetColumn) {
        const suggRes = await suggestTarget(activeFile.id);
        setSuggestedTarget(suggRes.suggested_target, suggRes.task_type);
        targetColumn = suggRes.suggested_target;
      }

      if (!targetColumn) {
        toast.error("Could not auto-detect target. Manual configuration required.", { id: tid });
        setTimeout(() => navigate('/prediction'), 1000);
        return;
      }

      const res = await autoPredict({
        file_id: activeFile.id,
        target_column: targetColumn,
        models: ['RandomForest', 'GradientBoosting']
      });

      addPredictionResult(res.structured_response);
      toast.success("Simulation Complete", { id: tid });
      setTimeout(() => navigate('/prediction'), 800);
    } catch (err) {
      toast.error("Simulation engine failed", { id: tid });
      setTimeout(() => navigate('/prediction'), 1000);
    } finally {
      setPredRunning(false);
    }
  };


  return (
    <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      {/* Header / KPI Row */}
      {!activeFile ? (
        <Card className="glass" style={{ padding: 40, overflow: 'hidden', position: 'relative' }}>
          <div className="opacity-5" style={{ position: 'absolute', top: 0, right: 0, padding: 40, pointerEvents: 'none' }}>
            <Brain size={240} />
          </div>
          <div style={{ position: 'relative', zIndex: 10 }}>
            <div>
              <h1 className="jakarta text-[2.75rem] font-extrabold text-white tracking-tight leading-tight mb-4">Terminal Presence: {user?.username}</h1>
              <p className="text-[#8899bb] text-base leading-relaxed max-w-[540px] mb-8 font-medium">
                Welcome to the Forensics Command. Ingest a dataset below to begin 
                AI-driven investigation or run high-fidelity simulations.
              </p>
              <div style={{ display: 'flex', gap: 16 }}>
                 <Badge variant="outline" style={{ padding: '4px 12px', borderColor: 'rgba(255,255,255,0.1)', color: 'rgba(255,255,255,0.4)' }}>
                   Vault: {userFiles.length} Assets
                 </Badge>
                 <Badge variant="outline" style={{ 
                   padding: '4px 12px', 
                   borderColor: 'rgba(255,255,255,0.1)', 
                   color: ollamaStatus.status === 'online' ? 'var(--green)' : 'var(--amber)'
                 }}>
                   Uplink: {ollamaStatus.status === 'online' ? 'Active' : 'Offline'}
                 </Badge>
              </div>
            </div>
          </div>
        </Card>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16 }}>
          <KPICard 
            icon={<Database size={16} />} label="Dossier Size"
            value={activeFile.rowCount?.toLocaleString() || '—'}
            sub={`${activeFile.colCount || 0} Dimensions Detected`}
            sparkData={[4, 7, 5, 8, 3, 9, 6]}
            trendUp={true}
          />
          <KPICard 
            icon={<Microscope size={16} />} label="Investigations"
            value={dashStats?.total_analyses || 0}
            sub={`${dashStats?.insights_found || 0} Critical Signals`}
            sparkData={[2, 4, 3, 5, 2, 6, 8]}
            trendUp={true}
          />
          <KPICard 
            icon={<TrendingUp size={16} />} label="Max Accuracy"
            value={dashStats?.best_accuracy ? `${(dashStats.best_accuracy * 100).toFixed(1)}%` : "—"}
            sub={dashStats?.best_model_name || "Simulation Required"}
            accentColor={dashStats?.best_accuracy > 0.8 ? 'var(--green)' : 'var(--cyan)'}
            trendUp={true}
          />
          <KPICard 
            icon={<Cpu size={16} />} label="Verified Signals"
            value={dashActivity?.patterns?.length || 0}
            sub="Active Intelligence Memory"
            sparkData={[30, 45, 40, 60, 55, 78, 85]}
            trendUp={true}
          />
        </div>
      )}

      {/* Action Panels (Active Only) */}
      {activeFile && (
        <div className="animate-slide-up" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
          {/* Analysis Action */}
          <div 
            onClick={handleQuickSummary}
            className="group glass"
            style={{ 
              cursor: 'pointer', padding: 40, 
              position: 'relative', overflow: 'hidden', transition: 'all 0.3s'
            }}
          >
            <div className="group-hover:scale-110" style={{ position: 'absolute', top: 0, right: 0, padding: 40, color: 'rgba(99, 102, 241, 0.1)', transition: 'all 0.3s' }}>
              <Microscope size={120} />
            </div>
            <div style={{ position: 'relative', zIndex: 10 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(124, 111, 255, 0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24 }}>
                <Sparkles size={24} color="#7c6fff" />
              </div>
              <h2 className="jakarta text-2xl font-extrabold text-white mb-2">Analysis Intelligence</h2>
              <p style={{ color: 'rgba(255,255,255,0.4)', marginBottom: 32, maxWidth: '320px' }}>
                Deploy analytical agents to scan the entire dataset and synthesize a 
                multi-section forensic dossier of findings.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#7c6fff', fontWeight: 800, letterSpacing: '0.12em', fontSize: 11, textTransform: 'uppercase' }}>
                {analysisRunning ? (
                  <><div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" /> Initializing...</>
                ) : (
                  <>Initialize Search <ChevronRight size={14} strokeWidth={3} /></>
                )}
              </div>
            </div>
          </div>

          {/* Prediction Action */}
          <div 
            onClick={handleAutoPredict}
            className="group glass"
            style={{ 
              cursor: 'pointer', padding: 40, 
              position: 'relative', overflow: 'hidden', transition: 'all 0.3s'
            }}
          >
            <div className="group-hover:scale-110" style={{ position: 'absolute', top: 0, right: 0, padding: 40, color: 'rgba(16, 185, 129, 0.1)', transition: 'all 0.3s' }}>
              <Cpu size={120} />
            </div>
            <div style={{ position: 'relative', zIndex: 10 }}>
              <div style={{ width: 48, height: 48, borderRadius: 12, background: 'rgba(124, 111, 255, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 24 }}>
                <TrendingUp size={24} color="#7c6fff" />
              </div>
              <h2 className="jakarta text-2xl font-extrabold text-white mb-2">Prediction Engine</h2>
              <p style={{ color: 'rgba(255,255,255,0.4)', marginBottom: 32, maxWidth: '320px' }}>
                Identify key target variables and launch automated model training 
                clusters to simulate future trajectories.
              </p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: '#7c6fff', fontWeight: 800, letterSpacing: '0.12em', fontSize: 11, textTransform: 'uppercase' }}>
                {predRunning ? (
                  <><div className="w-3 h-3 border-2 border-current border-t-transparent rounded-full animate-spin mr-1" /> Launching...</>
                ) : (
                  <>Launch Simulation <ChevronRight size={14} strokeWidth={3} /></>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Vault & Activity Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
        <Card className="glass" style={{ padding: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <SectionHeader label="Forensics Vault" />
            <div {...getRootProps()} style={{ cursor: 'pointer' }}>
              <input {...getInputProps()} />
              <Button size="sm" variant="outline" loading={isUploading} style={{ borderColor: 'rgba(255,255,255,0.1)' }}>
                <CloudUpload size={14} style={{ marginRight: 8 }} /> Ingest
              </Button>
            </div>
          </div>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            {userFiles.map(f => (
              <div 
                key={f.global_file_id}
                onClick={() => handleLoad(f.global_file_id, f.display_name)}
                style={{ 
                  display: 'flex', alignItems: 'center', gap: 16, padding: 16, 
                  borderRadius: 12, border: '1px solid', cursor: 'pointer', transition: 'all 0.2s',
                  background: activeFile?.id === f.global_file_id ? 'rgba(99, 102, 241, 0.05)' : 'rgba(255,255,255,0.05)',
                  borderColor: activeFile?.id === f.global_file_id ? 'rgba(99, 102, 241, 0.3)' : 'transparent'
                }}
              >
                <div style={{ padding: 8, borderRadius: 8, background: activeFile?.id === f.global_file_id ? 'rgba(99, 102, 241, 0.1)' : 'rgba(255,255,255,0.05)', color: activeFile?.id === f.global_file_id ? '#818cf8' : 'rgba(255,255,255,0.4)' }}>
                  <FileText size={18} />
                </div>
                <div style={{ flex: 1, overflow: 'hidden' }}>
                  <h4 style={{ fontSize: 13, fontWeight: 700 }} className="truncate">{f.display_name}</h4>
                  <p style={{ fontSize: 10, color: 'rgba(255,255,255,0.3)', textTransform: 'uppercase', letterSpacing: '-0.2px', marginTop: 2 }}>
                    {f.row_count.toLocaleString()} Rows · {f.detected_domain}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Intelligence Timeline */}
        <Card className="glass" style={{ padding: 24 }}>
          <SectionHeader label="Intelligence Timeline" />
          <div style={{ marginTop: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>

            {dashActivity?.activity?.length > 0 ? (
              dashActivity.activity.slice(0, 5).map((a, i) => (
                <div key={i} className="flex gap-4 group">
                  <div className="flex flex-col items-center">
                    <div className={`w-2 h-2 rounded-full mt-1.5 ${
                      a.type === 'analysis' ? 'bg-indigo-400' : 
                      a.type === 'prediction' ? 'bg-emerald-400' : 'bg-white/20'
                    }`} />
                    <div className="w-px h-full bg-white/5 my-1" />
                  </div>
                  <div>
                    <p className="text-xs text-white/80 group-hover:text-white transition-colors truncate max-w-[200px]">
                      {a.query || 'Analytical Event'}
                    </p>
                    <p className="text-[10px] text-white/20 uppercase tracking-widest mt-0.5">
                      {a.timestamp || 'Just now'}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <EmptyState icon={<History size={16}/>} title="Empty Feed" subtitle="No recent activity detected" />
            )}
          </div>
        </Card>
      </div>
      
      {/* Loading Overlay for Quick Run */}
      {(analysisRunning || predRunning) && (
        <div className="fixed inset-0 z-50 bg-[#0d0e12]/80 backdrop-blur-md flex flex-col items-center justify-center animate-fade-in">
          <div className="relative">
            <div className={`w-24 h-24 rounded-full border-4 border-indigo-500/10 border-t-indigo-500 animate-spin`} />
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="text-indigo-400 animate-pulse" />
            </div>
          </div>
          <h3 className="mt-8 text-xl font-bold syne tracking-widest uppercase">
            {analysisRunning ? 'Initializing Intelligence Uplink' : 'Launching Prediction Engine'}
          </h3>
          <p className="text-white/40 mt-2 animate-pulse font-mono text-sm">
            {analysisRunning ? 'Synthesizing forensic vectors...' : 'Calibrating neural trajectory...'}
          </p>
        </div>
      )}
    </div>
  );
}
