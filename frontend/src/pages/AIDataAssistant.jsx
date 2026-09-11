import React, { useState, useRef, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { 
  FiUpload, 
  FiSend, 
  FiDownload, 
  FiDatabase, 
  FiMessageCircle,
  FiBarChart2,
  FiFileText,
  FiRefreshCw,
  FiInfo,
  FiTrendingUp,
  FiFilter,
  FiEdit3,
  FiAlertTriangle,
  FiKey,
  FiCheck,
  FiCopy,
  FiTrash2,
  FiZap,
  FiHelpCircle,
  FiMaximize2,
  FiImage
} from 'react-icons/fi';
import { HiSparkles } from 'react-icons/hi';
import { BsRobot, BsCpu, BsLightningChargeFill } from 'react-icons/bs';
import { toast, Toaster } from 'react-hot-toast';
import { API_BASE_URL } from '../config.js';

export default function AIDataAssistant() {
  const [searchParams] = useSearchParams();
  const promptParam = searchParams.get('prompt');
  
  const [dataset, setDataset] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      isGroq: true,
      agentName: 'Abhimanyu',
      content: "👋 Greetings! I am **Abhimanyu**, your Autonomous AI Data Agent powered by **Groq Ultra-Fast LLM Intelligence** and multivariate statistical engines.\n\nI can analyze your dataset, isolate outliers, answer natural language inquiries, **generate visual graphs on demand**, and produce **detailed Black & White audit PDF reports with borders and embedded charts**.\n\n💡 **Suggested Actions:**\n• Click **'Load Demo (district_health.csv)'** on the left to activate our benchmark dataset\n• Or click any question in the **'Suggested Questions'** panel below!",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  // Groq API Configuration State
  const [groqStatus, setGroqStatus] = useState({ configured: true, primary_model: 'qwen/qwen3.8-27b' });
  const [groqKeyInput, setGroqKeyInput] = useState('');
  const [showKeyModal, setShowKeyModal] = useState(false);
  const [isSavingKey, setIsSavingKey] = useState(false);
  const [zoomedImage, setZoomedImage] = useState(null);
  
  // Suggested Questions State
  const [suggestedQuestions, setSuggestedQuestions] = useState([
    "Which districts show unusual healthcare patterns?",
    "Show graph and visualize key anomalies as per my problem statement",
    "Generate a detailed black and white PDF report summary of this dataset with borders and graph",
    "Which districts have the highest infant mortality and lowest doctor density?",
    "What is the correlation between electricity access and institutional delivery?",
    "Generate an executive HTML report summary of this dataset"
  ]);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check Groq status on mount
  useEffect(() => {
    fetchGroqStatus();
    fetchSuggestedQuestions();
  }, []);

  // If URL contains prompt parameter, auto load sample and execute query
  useEffect(() => {
    if (promptParam && !dataset) {
      handleLoadSample(promptParam);
    }
  }, [promptParam]);

  const fetchGroqStatus = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/groq/status`);
      if (res.ok) {
        const data = await res.json();
        setGroqStatus(data);
      }
    } catch (err) {
      console.warn('Could not fetch Groq status:', err);
    }
  };

  const fetchSuggestedQuestions = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/groq/suggested-questions`);
      if (res.ok) {
        const data = await res.json();
        if (data.questions && data.questions.length > 0) {
          setSuggestedQuestions(data.questions);
        }
      }
    } catch (err) {
      console.warn('Could not fetch suggested questions:', err);
    }
  };

  const handleSaveGroqKey = async () => {
    if (!groqKeyInput.trim()) {
      toast.error('Please enter a valid Groq API key (starts with gsk_...)');
      return;
    }
    setIsSavingKey(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/groq/configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: groqKeyInput.trim() })
      });
      const data = await res.json();
      if (data.success) {
        toast.success('⚡ Groq API Key connected! Abhimanyu AI is active.');
        setGroqStatus(prev => ({ ...prev, configured: true }));
        setShowKeyModal(false);
        setGroqKeyInput('');
      } else {
        toast.error(data.error || 'Failed to configure Groq key');
      }
    } catch (err) {
      toast.error('Failed to connect to Groq service');
    } finally {
      setIsSavingKey(false);
    }
  };

  const handleLoadSample = async (customPrompt = null) => {
    setIsUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ai-assistant/load-sample`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      });
      const data = await response.json();
      if (data.success) {
        setDataset({
          filename: data.filename,
          summary: data.summary,
          preview: data.preview
        });

        const newMessage = {
          id: Date.now(),
          type: 'assistant',
          isGroq: true,
          agentName: 'Abhimanyu',
          content: `✅ **Demonstration Dataset Activated: district_health.csv** (India Open Government Data)\n\n📊 **Dataset Parameters:**\n• **Records:** ${data.summary.basic_info.rows.toLocaleString()} districts across 12 states\n• **Indicators:** ${data.summary.basic_info.columns} quantitative health & infrastructure metrics\n• **Known Outliers:** Severe divergence in Shrawasti, Wayanad, Gadchiroli, and Barmer\n\n💡 Ask me to **'Show graph and visualize'** or click any question below!`,
          timestamp: new Date(),
          data: data.summary
        };

        setMessages(prev => [...prev, newMessage]);
        toast.success('Demonstration dataset district_health.csv loaded!');
        fetchSuggestedQuestions();

        if (customPrompt) {
          executeChatQuery(customPrompt);
        }
      } else {
        toast.error(data.error || 'Failed to load sample dataset');
      }
    } catch (err) {
      console.error('Load sample error:', err);
      toast.error('Failed to load sample dataset');
    } finally {
      setIsUploading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });

      const data = await response.json();

      if (data.success) {
        setDataset({
          filename: file.name,
          summary: {
            basic_info: {
              rows: data.summary.rows,
              columns: data.summary.column_names.length,
              size_mb: (file.size / (1024 * 1024)).toFixed(2)
            },
            columns: data.summary.column_names.map(name => ({
              name,
              type: data.summary.data_types[name] || 'object'
            }))
          },
          preview: []
        });

        const newMessage = {
          id: Date.now(),
          type: 'assistant',
          isGroq: true,
          agentName: 'Abhimanyu',
          content: `✅ **Dataset Uploaded: ${file.name}**\n\n• **Records:** ${data.summary.rows.toLocaleString()}\n• **Columns:** ${data.summary.column_names.length}\n• **Key Columns:** ${data.summary.column_names.slice(0, 6).join(', ')}...\n\nI have parsed the statistical context. Ask me anything, request visualizations, or generate audit reports!`,
          timestamp: new Date()
        };

        setMessages(prev => [...prev, newMessage]);
        toast.success(`Uploaded ${file.name}`);
        fetchSuggestedQuestions();
      } else {
        toast.error(data.error || 'Failed to upload file');
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload file');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const executeChatQuery = async (queryText) => {
    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: queryText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Send chat request to backend (routes to Abhimanyu via Groq API)
      const response = await fetch(`${API_BASE_URL}/api/groq/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: queryText,
          history: messages.slice(-4).map(m => ({ role: m.type === 'user' ? 'user' : 'assistant', content: m.content }))
        }),
        credentials: 'include'
      });

      const data = await response.json();

      if (data.success) {
        const assistantMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: data.response,
          isGroq: true,
          agentName: data.agent_name || 'Abhimanyu',
          model: data.model || groqStatus.primary_model,
          timestamp: new Date(),
          messageType: data.type,
          chart: data.chart,
          report: data.report,
          downloadAvailable: data.download_available,
          downloadUrl: data.download_url,
          filename: data.filename
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          type: 'assistant',
          content: `❌ **Error:** ${data.error || 'Failed to process request'}`,
          timestamp: new Date(),
          messageType: 'error'
        };
        setMessages(prev => [...prev, errorMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        type: 'assistant',
        content: '❌ **Notice:** Connection issue with the server. Please verify backend connectivity.',
        timestamp: new Date(),
        messageType: 'error'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim() || isLoading) return;
    const textToSend = inputMessage;
    setInputMessage('');
    if (!dataset) {
      handleLoadSample(textToSend);
    } else {
      executeChatQuery(textToSend);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const clearChatHistory = () => {
    setMessages([
      {
        id: Date.now(),
        type: 'assistant',
        isGroq: true,
        agentName: 'Abhimanyu',
        content: "🧹 Chat history cleared. What would you like to explore next in your dataset?",
        timestamp: new Date()
      }
    ]);
    toast.success('Chat history cleared');
  };

  const formatMessage = (content) => {
    if (!content) return '';
    return content
      .replace(/### (.*?)\n/g, '<h3 class="text-sm font-bold text-gray-900 mt-2.5 mb-1">$1</h3>')
      .replace(/#### (.*?)\n/g, '<h4 class="text-xs font-semibold text-gray-800 mt-2 mb-1">$1</h4>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 py-0.5 rounded text-xs text-purple-700 font-mono">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  return (
    <>
      <Toaster position="top-right" />

      {/* Fullscreen Image Lightbox Modal */}
      {zoomedImage && (
        <div 
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4 cursor-pointer"
          onClick={() => setZoomedImage(null)}
        >
          <div className="relative max-w-4xl w-full max-h-[90vh] bg-white rounded-2xl p-4 shadow-2xl" onClick={e => e.stopPropagation()}>
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-gray-200">
              <span className="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                <FiBarChart2 className="text-blue-600" />
                Abhimanyu Visual Analytics (High Resolution)
              </span>
              <button 
                onClick={() => setZoomedImage(null)}
                className="text-gray-400 hover:text-gray-600 text-sm font-bold p-1 cursor-pointer"
              >
                ✕ Close
              </button>
            </div>
            <img src={zoomedImage} alt="Zoomed Plot" className="w-full h-auto max-h-[75vh] object-contain rounded-lg border" />
          </div>
        </div>
      )}
      
      <div className="min-h-screen bg-slate-50 p-4 pt-20 pb-8 flex flex-col">
        <div className="max-w-7xl mx-auto w-full flex-1 flex flex-col">
          
          {/* Header Bar */}
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4 mb-4 flex flex-col md:flex-row md:items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-xl bg-gradient-to-tr from-blue-700 to-indigo-800 flex items-center justify-center text-white shadow-md">
                <BsRobot className="w-6 h-6" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                  Abhimanyu
                  <span className="text-xs bg-indigo-50 text-indigo-700 px-2.5 py-0.5 rounded-full font-semibold border border-indigo-100">
                    Autonomous AI Data Agent
                  </span>
                </h1>
                <p className="text-xs text-gray-500">
                  Descriptive analysis, on-demand visualization, and black & white audit reports
                </p>
              </div>
            </div>

            {/* Abhimanyu Engine Status Badge */}
            <div className="flex items-center gap-2 px-3.5 py-2 rounded-xl border text-xs font-semibold bg-emerald-50 border-emerald-200 text-emerald-800 shadow-2xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Abhimanyu Neural Engine Active</span>
            </div>
          </div>

          {/* Main 2-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 flex-1">
            
            {/* Left Column: Dataset Management & Schema (4 cols) */}
            <div className="lg:col-span-4 space-y-4 flex flex-col">
              
              {/* Dataset Box */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5">
                <h3 className="text-sm font-bold text-gray-900 mb-3 flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <FiDatabase className="text-blue-600" />
                    Active Dataset
                  </span>
                  {dataset && (
                    <span className="text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-100">
                      Loaded
                    </span>
                  )}
                </h3>

                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".csv,.xlsx,.xls,.json"
                  className="hidden"
                />

                <div className="space-y-2">
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    disabled={isUploading}
                    className="w-full bg-slate-900 hover:bg-slate-800 text-white py-2.5 px-3 rounded-xl text-xs font-semibold flex items-center justify-center gap-2 transition cursor-pointer shadow-sm disabled:opacity-50"
                  >
                    {isUploading ? (
                      <>
                        <FiRefreshCw className="animate-spin w-4 h-4" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <FiUpload className="w-4 h-4" />
                        Upload CSV / Excel
                      </>
                    )}
                  </button>

                  <button
                    onClick={() => handleLoadSample()}
                    disabled={isUploading}
                    className="w-full bg-gradient-to-r from-amber-50 to-orange-50 hover:from-amber-100 hover:to-orange-100 border border-amber-200 text-amber-900 py-2.5 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-2 transition cursor-pointer"
                  >
                    <HiSparkles className="text-amber-600 w-4 h-4" />
                    Load Demo (district_health.csv)
                  </button>
                </div>

                {dataset ? (
                  <div className="mt-4 p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-gray-900 truncate max-w-[180px]" title={dataset.filename}>
                        📄 {dataset.filename}
                      </span>
                      <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-medium">
                        SQLite Stored
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center pt-2">
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <div className="text-[10px] text-gray-500">Rows</div>
                        <div className="text-xs font-bold text-gray-900">{dataset.summary.basic_info.rows.toLocaleString()}</div>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <div className="text-[10px] text-gray-500">Cols</div>
                        <div className="text-xs font-bold text-gray-900">{dataset.summary.basic_info.columns}</div>
                      </div>
                      <div className="bg-white p-2 rounded-lg border border-slate-200">
                        <div className="text-[10px] text-gray-500">Size</div>
                        <div className="text-xs font-bold text-gray-900">{dataset.summary.basic_info.size_mb} MB</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="mt-3 p-3 bg-blue-50/70 rounded-xl border border-blue-100 text-xs text-blue-800">
                    💡 Click <strong>Load Demo</strong> to test with India Open Government district health data.
                  </div>
                )}
              </div>

              {/* Dataset Columns Schema */}
              {dataset && dataset.summary && dataset.summary.columns && (
                <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-5 flex-1 flex flex-col max-h-[360px]">
                  <h4 className="text-xs font-bold text-gray-700 uppercase tracking-wider mb-2 flex items-center justify-between">
                    <span>Dataset Schema ({dataset.summary.columns.length})</span>
                    <span className="text-[10px] text-gray-400 font-normal">Click to insert</span>
                  </h4>
                  <div className="space-y-1.5 overflow-y-auto flex-1 pr-1">
                    {dataset.summary.columns.map((col, idx) => (
                      <button
                        key={idx}
                        onClick={() => setInputMessage(prev => `${prev} ${col.name}`.trim())}
                        className="w-full text-left p-2 rounded-lg hover:bg-slate-50 border border-transparent hover:border-slate-200 transition flex items-center justify-between group cursor-pointer text-xs"
                      >
                        <span className="font-mono font-medium text-gray-800 truncate max-w-[170px]" title={col.name}>
                          {col.name}
                        </span>
                        <span className="text-[10px] text-gray-400 group-hover:text-indigo-600 bg-gray-100 px-1.5 py-0.5 rounded font-mono">
                          {col.type}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Right Column: Suggested Questions & Chat (8 cols) */}
            <div className="lg:col-span-8 flex flex-col space-y-3">
              
              {/* Dedicated Questions Section */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-4">
                <div className="flex items-center justify-between mb-2.5">
                  <div className="flex items-center gap-2">
                    <div className="p-1.5 bg-amber-100 text-amber-700 rounded-lg">
                      <FiHelpCircle className="w-4 h-4" />
                    </div>
                    <h3 className="text-sm font-bold text-gray-900">
                      Suggested Questions for Abhimanyu
                    </h3>
                  </div>
                  <span className="text-xs text-gray-500 font-medium">
                    Click any question to ask immediately
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {suggestedQuestions.map((q, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        if (dataset) {
                          executeChatQuery(q);
                        } else {
                          handleLoadSample(q);
                        }
                      }}
                      className="text-left p-2.5 rounded-xl border border-slate-200 hover:border-indigo-400 bg-slate-50 hover:bg-indigo-50/40 transition duration-150 flex items-start gap-2 text-xs text-gray-700 hover:text-gray-900 font-medium cursor-pointer group"
                    >
                      <span className="text-indigo-600 group-hover:translate-x-0.5 transition-transform flex-shrink-0 mt-0.5">
                        ➔
                      </span>
                      <span className="line-clamp-2">{q}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Chat Container */}
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 flex-1 flex flex-col min-h-[480px] overflow-hidden">
                
                {/* Chat Header */}
                <div className="px-5 py-3 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                  <div className="flex items-center gap-2">
                    <FiMessageCircle className="text-blue-600 w-4 h-4" />
                    <span className="text-xs font-bold text-gray-800">Abhimanyu AI Chat</span>
                    <span className="text-[10px] bg-amber-100 text-amber-900 px-2 py-0.5 rounded font-mono font-semibold flex items-center gap-1">
                      <BsLightningChargeFill className="text-amber-600" />
                      Groq Powered
                    </span>
                  </div>
                  
                  <button
                    onClick={clearChatHistory}
                    title="Clear Chat History"
                    className="text-xs text-gray-400 hover:text-red-500 flex items-center gap-1 p-1 rounded transition cursor-pointer"
                  >
                    <FiTrash2 className="w-3.5 h-3.5" />
                    <span>Clear</span>
                  </button>
                </div>

                {/* Messages List */}
                <div className="flex-1 overflow-y-auto p-5 space-y-4 max-h-[520px]">
                  {messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[88%] rounded-2xl p-4 shadow-2xs ${
                          msg.type === 'user'
                            ? 'bg-gradient-to-r from-blue-700 to-indigo-700 text-white rounded-br-xs'
                            : 'bg-slate-100 text-gray-800 rounded-bl-xs border border-slate-200/80'
                        }`}
                      >
                        {/* Message Header */}
                        <div className="flex items-center justify-between gap-2 mb-2 pb-1 border-b border-black/5 text-[11px] opacity-80">
                          <span className="font-semibold flex items-center gap-1">
                            {msg.type === 'user' ? (
                              'You'
                            ) : (
                              <>
                                <BsRobot className="text-indigo-600" />
                                <strong>Abhimanyu AI</strong>
                                <span className="text-[10px] opacity-60 font-mono">({msg.model || 'Groq'})</span>
                              </>
                            )}
                          </span>
                          
                          {msg.type === 'assistant' && (
                            <button
                              onClick={() => copyToClipboard(msg.content)}
                              className="hover:text-blue-600 flex items-center gap-0.5 cursor-pointer"
                              title="Copy response text"
                            >
                              <FiCopy className="w-3 h-3" />
                            </button>
                          )}
                        </div>

                        {/* Content */}
                        <div
                          className="prose prose-sm max-w-none text-xs leading-relaxed text-inherit"
                          dangerouslySetInnerHTML={{ __html: formatMessage(msg.content) }}
                        />

                        {/* Embedded Chart / Visualization Card */}
                        {msg.chart && (
                          <div className="mt-4 p-3 bg-white rounded-xl border border-slate-300 shadow-sm text-gray-800">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                                <FiBarChart2 className="text-indigo-600" />
                                {msg.chart.title || 'Abhimanyu Visual Analytics'}
                              </span>
                              <div className="flex items-center gap-1.5">
                                <button
                                  onClick={() => setZoomedImage(msg.chart.base64 || `${API_BASE_URL}${msg.chart.download_url}`)}
                                  className="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2 py-1 rounded font-medium flex items-center gap-1 transition cursor-pointer"
                                  title="Zoom / Fullscreen"
                                >
                                  <FiMaximize2 className="w-3 h-3" />
                                  Expand
                                </button>
                                <a
                                  href={msg.chart.base64 || `${API_BASE_URL}${msg.chart.download_url}`}
                                  download={msg.chart.filename || 'visualization.png'}
                                  className="text-[11px] bg-indigo-50 hover:bg-indigo-100 text-indigo-700 px-2 py-1 rounded font-medium flex items-center gap-1 transition cursor-pointer"
                                  title="Download PNG"
                                >
                                  <FiDownload className="w-3 h-3" />
                                  PNG
                                </a>
                              </div>
                            </div>
                            <div 
                              className="rounded-lg overflow-hidden border border-slate-200 bg-white cursor-pointer group relative"
                              onClick={() => setZoomedImage(msg.chart.base64 || `${API_BASE_URL}${msg.chart.download_url}`)}
                            >
                              <img
                                src={msg.chart.base64 || `${API_BASE_URL}${msg.chart.download_url}`}
                                alt="Dataset Visualization"
                                className="w-full h-auto max-h-[360px] object-contain group-hover:opacity-95 transition"
                              />
                              <div className="absolute bottom-2 right-2 bg-black/70 text-white text-[10px] px-2 py-0.5 rounded backdrop-blur-xs flex items-center gap-1 opacity-0 group-hover:opacity-100 transition">
                                <FiMaximize2 className="w-2.5 h-2.5" /> Click to expand
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Black & White Audit PDF / HTML Report Card */}
                        {(msg.report || (msg.downloadAvailable && msg.downloadUrl)) && (
                          <div className="mt-4 p-3 bg-black text-white rounded-xl shadow-md border border-neutral-800">
                            <div className="flex items-center justify-between flex-wrap gap-2">
                              <div>
                                <div className="text-xs font-bold flex items-center gap-1.5 text-white">
                                  <FiFileText className="text-amber-400" />
                                  {msg.report?.format === 'pdf' ? 'Black & White Themed PDF Audit Report' : (msg.filename || 'Executive Report')}
                                </div>
                                <div className="text-[10px] text-gray-400 mt-0.5">
                                  Format: {msg.report?.format?.toUpperCase() || 'PDF'} | Solid Borders & Embedded Visualizations | Verified by Abhimanyu AI
                                </div>
                              </div>
                              <a
                                href={`${API_BASE_URL}${msg.report?.download_url || msg.downloadUrl}`}
                                download={msg.report?.filename || msg.filename}
                                target="_blank"
                                rel="noreferrer"
                                className="px-3 py-1.5 bg-white text-black hover:bg-neutral-200 text-xs font-bold rounded-lg shadow transition flex items-center gap-1.5 cursor-pointer"
                              >
                                <FiDownload className="w-3.5 h-3.5" />
                                Download {msg.report?.format?.toUpperCase() || 'Report'}
                              </a>
                            </div>
                          </div>
                        )}

                        <div className="text-[10px] opacity-60 text-right mt-1">
                          {msg.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </div>
                      </div>
                    </div>
                  ))}

                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-slate-100 rounded-2xl rounded-bl-xs p-4 border border-slate-200 text-xs text-gray-600 flex items-center gap-2.5">
                        <FiRefreshCw className="animate-spin text-indigo-600 w-4 h-4" />
                        <span>Abhimanyu AI is processing request via Groq...</span>
                      </div>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Input Controls */}
                <div className="p-3 border-t border-slate-100 bg-white">
                  
                  {/* Quick Action Pills */}
                  <div className="flex items-center gap-1.5 mb-2 overflow-x-auto pb-1 text-xs">
                    <span className="text-[10px] text-gray-400 font-semibold uppercase tracking-wider mr-1">Quick:</span>
                    <button
                      onClick={() => executeChatQuery("Show graph and visualize the healthcare anomalies across districts as per problem statement")}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-gray-700 rounded-lg text-xs font-medium transition cursor-pointer flex items-center gap-1"
                    >
                      <FiBarChart2 className="w-3 h-3 text-indigo-600" />
                      Show Graph
                    </button>
                    <button
                      onClick={() => executeChatQuery("Generate a detailed black and white PDF report summary of this dataset with borders and graph")}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-gray-700 rounded-lg text-xs font-medium transition cursor-pointer flex items-center gap-1"
                    >
                      <FiFileText className="w-3 h-3 text-black" />
                      B&W PDF Report
                    </button>
                    <button
                      onClick={() => executeChatQuery("Which districts show unusual healthcare patterns?")}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-gray-700 rounded-lg text-xs font-medium transition cursor-pointer flex items-center gap-1"
                    >
                      <FiAlertTriangle className="w-3 h-3 text-amber-600" />
                      Anomalies
                    </button>
                    <button
                      onClick={() => executeChatQuery("Generate an executive HTML report summary of this dataset")}
                      className="px-2.5 py-1 bg-slate-100 hover:bg-indigo-50 hover:text-indigo-700 text-gray-700 rounded-lg text-xs font-medium transition cursor-pointer flex items-center gap-1"
                    >
                      <FiDownload className="w-3 h-3 text-emerald-600" />
                      HTML Report
                    </button>
                  </div>

                  <div className="flex gap-2">
                    <textarea
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyDown={handleKeyPress}
                      rows="2"
                      placeholder="Ask Abhimanyu anything, request graphs, or generate B&W audit reports..."
                      disabled={isLoading}
                      className="flex-1 resize-none border border-slate-300 rounded-xl px-3.5 py-2.5 text-xs text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-slate-50/50"
                    />

                    <button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim() || isLoading}
                      className="px-4 bg-gradient-to-tr from-blue-700 to-indigo-800 hover:from-blue-800 hover:to-indigo-900 text-white rounded-xl font-semibold shadow-md transition disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center cursor-pointer"
                    >
                      <FiSend className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center justify-between text-[11px] text-gray-400 mt-2 px-1">
                    <span>Press <strong>Enter</strong> to send, <strong>Shift+Enter</strong> for new line</span>
                    <span className="flex items-center gap-1">
                      <FiZap className="text-amber-500 w-3 h-3" />
                      Abhimanyu AI Engine Active
                    </span>
                  </div>
                </div>

              </div>

            </div>

          </div>

        </div>
      </div>
    </>
  );
}