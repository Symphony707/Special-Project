import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

const useStore = create(
  persist(
    (set) => ({
      // Auth
      user: null,
      loading: true,
      setUser: (user) => set({ user }),
      setLoading: (loading) => set({ loading }),
      logout: () => {
        set({ user: null, activeFile: null, chatHistory: [] })
        localStorage.removeItem('datamind-storage') // Complete wipe on logout
      },

      // Files & Assets
      userFiles: [],
      activeFile: null,
      setUserFiles: (files) => set({ userFiles: files }),
      setActiveFile: (id, name, details={}) => set({ 
        activeFile: id ? { id, name, ...details } : null 
      }),

      // Dashboard Stats & Activity
      dashStats: null,
      dashActivity: { patterns: [], activity: [] },
      setDashStats: (stats) => set({ dashStats: stats }),
      setDashActivity: (activity) => set({ dashActivity: activity }),

      // Analysis Lab Artifacts
      labArtifacts: [],
      setLabArtifacts: (artifacts) => set({ labArtifacts: artifacts }),
      addLabArtifact: (art) => set((s) => ({ 
        labArtifacts: [art, ...s.labArtifacts] 
      })),

      // Chat & Analysis Lab
      chatHistory: [],
      addChatMessage: (msg) => set((state) => ({ 
        chatHistory: [...state.chatHistory, msg] 
      })),
      clearChat: () => set({ chatHistory: [] }),
      ollamaOnline: true,

      // NEW: Dashboard & Lab State
      dashboardAnalysis: null,
      dashboardPrediction: null,
      suggestedTarget: {
        target: null,
        taskType: 'classification'
      },
      setDashboardAnalysis: (res) => set({ dashboardAnalysis: res }),
      setDashboardPrediction: (res) => set({ dashboardPrediction: res }),
      setSuggestedTarget: (target, taskType) => set({ 
        suggestedTarget: { target, taskType } 
      }),

      analysisResults: [],   // History of structured analysis reports
      predictionResults: [], // History of predictive runs
      addAnalysisResult: (res) => set(state => ({ 
        analysisResults: [res, ...state.analysisResults].slice(0, 5) 
      })),
      addPredictionResult: (res) => set(state => ({ 
        predictionResults: [res, ...state.predictionResults].slice(0, 5) 
      })),


      // Prediction Results
      predictionResult: null,
      setPredictionResult: (res) => set({ predictionResult: res }),

      // Application Settings
      settings: {
        darkMode: true,
        animations: true,
        notifications: true,
        computationTier: 'Deep'
      },
      setSettings: (newSettings) => set((state) => ({ 
        settings: { ...state.settings, ...newSettings } 
      })),
    }),
    {
      name: 'datamind-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ 
        user: state.user, 
        settings: state.settings,
        activeFile: state.activeFile,
        analysisResults: state.analysisResults,
        predictionResults: state.predictionResults,
        chatHistory: state.chatHistory
      }), 
    }
  )
)

export default useStore
