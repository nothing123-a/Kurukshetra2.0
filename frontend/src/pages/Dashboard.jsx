import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  FiDatabase, FiZap, FiShield, FiTrendingUp, 
  FiCheckCircle, FiBarChart, FiFileText, FiDownload, FiPlus, FiEye,
  FiAlertTriangle, FiSearch, FiLayers, FiHelpCircle, FiArrowRight
} from 'react-icons/fi'
import { HiSparkles } from 'react-icons/hi'
import { BsRobot, BsLightbulb } from 'react-icons/bs'
import { API_BASE_URL } from '../config.js'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const navigate = useNavigate()

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/dashboard`, {
        method: 'GET',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' }
      })
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    }
  }

  const handleLaunchDemo = async () => {
    setDemoLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai-assistant/load-sample`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      const data = await response.json()
      if (data.success) {
        navigate('/ai-assistant?prompt=' + encodeURIComponent('Which districts show unusual healthcare patterns?'))
      } else {
        navigate('/ai-assistant')
      }
    } catch (err) {
      navigate('/ai-assistant')
    } finally {
      setDemoLoading(false)
    }
  }

  const solutionCapabilities = [
    {
      icon: FiSearch,
      title: '1. Inspect Dataset',
      description: 'Instant overview of rows, columns, memory size, data types, and data completeness metrics.',
      color: '#3B82F6'
    },
    {
      icon: FiFileText,
      title: '2. Understand Columns',
      description: 'Semantic schema inference categorizing numerical, categorical, and geographic identifier columns.',
      color: '#8B5CF6'
    },
    {
      icon: FiZap,
      title: '3. Clean Data',
      description: 'Automated deduplication, missing value imputation (mean/median/mode), and format sanitization.',
      color: '#10B981'
    },
    {
      icon: FiLayers,
      title: '4. Select Analysis',
      description: 'Autonomous selection of relevant statistical tests, correlations, and multivariate clustering.',
      color: '#F59E0B'
    },
    {
      icon: FiBarChart,
      title: '5. Generate Statistics',
      description: 'Comprehensive descriptive metrics including means, medians, dispersion, IQR, and distribution skewness.',
      color: '#EC4899'
    },
    {
      icon: FiAlertTriangle,
      title: '6. Identify Anomalies',
      description: 'Multivariate statistical outlier detection isolating abnormal entities and unusual pattern clusters.',
      color: '#EF4444'
    },
    {
      icon: FiTrendingUp,
      title: '7. Create Visualizations',
      description: 'Automated generation of distribution plots, correlation heatmaps, and metric comparison charts.',
      color: '#06B6D4'
    },
    {
      icon: BsLightbulb,
      title: '8. Explain Findings & Report',
      description: 'Natural language synthesis explaining key patterns, root causes, and exportable stakeholder reports.',
      color: '#84CC16'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-700 via-indigo-600 to-purple-700 rounded-2xl p-8 mb-8 text-white relative overflow-hidden shadow-xl">
          <div className="absolute top-0 right-0 opacity-10 pointer-events-none">
            <BsRobot style={{ fontSize: '240px' }} />
          </div>
          
          <div className="flex items-center justify-between flex-wrap gap-6 relative z-10">
            <div className="flex-1 max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold uppercase tracking-wider mb-4 border border-white/20">
                <HiSparkles className="text-yellow-300" />
                Agentic AI + Data Science
              </div>
              <h1 className="text-4xl font-extrabold tracking-tight mb-3">
                Bhishma's Autonomous Data Intelligence Agent
              </h1>
              <p className="text-lg opacity-90 leading-relaxed mb-6">
                Enabling non-technical users to autonomously inspect large CSV/Excel datasets, understand columns, clean data, compute statistics, detect anomalies, and generate actionable insights in plain natural language.
              </p>
              
              <div className="flex gap-4 flex-wrap">
                <button
                  onClick={() => navigate('/upload')}
                  className="flex items-center gap-2 px-6 py-3 bg-white text-blue-700 hover:bg-blue-50 rounded-xl font-bold transition-all shadow-md hover:shadow-lg cursor-pointer"
                >
                  <FiPlus />
                  Upload Your Dataset
                </button>
                <button
                  onClick={() => navigate('/ai-assistant')}
                  className="flex items-center gap-2 px-6 py-3 bg-white/20 hover:bg-white/30 border border-white/30 text-white rounded-xl font-semibold transition-all backdrop-blur-sm cursor-pointer"
                >
                  <BsRobot />
                  Open AI Agent Chat
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Expected Demonstration Banner */}
        <div className="bg-gradient-to-r from-amber-50 to-orange-50 rounded-2xl p-6 mb-8 border-2 border-amber-300 shadow-sm relative">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6">
            <div className="flex-1">
              <div className="flex items-center gap-2 text-amber-800 font-bold text-sm uppercase tracking-wide mb-1">
                <HiSparkles className="text-amber-600 text-lg" />
                Expected Demonstration Scenario
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">
                India Open Government Data Platform: <span className="text-blue-700 font-mono">district_health.csv</span>
              </h3>
              <p className="text-gray-700 text-sm mb-3 leading-relaxed">
                Demonstrates autonomous dataset inspection, statistical outlier calculation, and natural language explanation for non-technical administrators.
              </p>
              <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-lg border border-amber-200 text-sm font-mono text-gray-800 shadow-inner">
                <span className="text-gray-500 font-sans font-medium">Prompt:</span>
                <span className="font-semibold text-blue-600">"Which districts show unusual healthcare patterns?"</span>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row gap-3 w-full lg:w-auto">
              <button
                onClick={handleLaunchDemo}
                disabled={demoLoading}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white font-bold rounded-xl shadow-md hover:shadow-lg transition-all cursor-pointer whitespace-nowrap"
              >
                <BsRobot className="text-lg" />
                {demoLoading ? 'Loading Demo Dataset...' : 'Run Demonstration Query'}
                <FiArrowRight />
              </button>
            </div>
          </div>
        </div>

        {/* 8-Step Solution Pillars */}
        <div className="mb-10">
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              Autonomous Analytical Capabilities
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Full-lifecycle autonomous data analysis engineered to deliver enterprise insights from raw tabular data without requiring technical expertise.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {solutionCapabilities.map((cap, idx) => {
              const Icon = cap.icon
              return (
                <div 
                  key={idx}
                  className="bg-white rounded-xl p-6 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-200 hover:-translate-y-1"
                >
                  <div 
                    className="w-12 h-12 rounded-xl flex items-center justify-center mb-4 text-xl"
                    style={{ backgroundColor: `${cap.color}15`, color: cap.color }}
                  >
                    <Icon />
                  </div>
                  <h3 className="font-bold text-gray-900 text-lg mb-2">
                    {cap.title}
                  </h3>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {cap.description}
                  </p>
                </div>
              )
            })}
          </div>
        </div>

        {/* Quick Access Workflow */}
        <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm mb-8">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <FiZap className="text-blue-600" />
            Quick Navigation & Tools
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/upload')}
              className="p-5 text-left bg-blue-50/50 hover:bg-blue-50 border border-blue-100 rounded-xl transition-all cursor-pointer group"
            >
              <FiDatabase className="text-2xl text-blue-600 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-bold text-gray-900">Upload Dataset</div>
              <div className="text-xs text-gray-500 mt-1">Load CSV, Excel, or JSON files for instant schema analysis.</div>
            </button>

            <button
              onClick={() => navigate('/ai-assistant')}
              className="p-5 text-left bg-purple-50/50 hover:bg-purple-50 border border-purple-100 rounded-xl transition-all cursor-pointer group"
            >
              <BsRobot className="text-2xl text-purple-600 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-bold text-gray-900">AI Data Assistant</div>
              <div className="text-xs text-gray-500 mt-1">Ask questions, request anomaly detection, and filter data.</div>
            </button>

            <button
              onClick={() => navigate('/outliers')}
              className="p-5 text-left bg-rose-50/50 hover:bg-rose-50 border border-rose-100 rounded-xl transition-all cursor-pointer group"
            >
              <FiAlertTriangle className="text-2xl text-rose-600 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-bold text-gray-900">Anomaly Detection</div>
              <div className="text-xs text-gray-500 mt-1">Inspect IQR outliers and isolated abnormal entities.</div>
            </button>

            <button
              onClick={() => navigate('/analytics')}
              className="p-5 text-left bg-emerald-50/50 hover:bg-emerald-50 border border-emerald-100 rounded-xl transition-all cursor-pointer group"
            >
              <FiTrendingUp className="text-2xl text-emerald-600 mb-2 group-hover:scale-110 transition-transform" />
              <div className="font-bold text-gray-900">Visual Analytics</div>
              <div className="text-xs text-gray-500 mt-1">Explore distributions, correlation heatmaps, and summaries.</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}