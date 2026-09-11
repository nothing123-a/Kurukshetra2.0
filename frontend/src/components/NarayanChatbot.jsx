import React, { useState, useRef, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  FiUpload, 
  FiSend, 
  FiDownload, 
  FiDatabase, 
  FiFileText, 
  FiRefreshCw, 
  FiLock, 
  FiTrash2, 
  FiHelpCircle,
  FiMinimize2,
  FiMaximize2,
  FiX,
  FiCheckCircle,
  FiZap,
  FiLayers
} from 'react-icons/fi';
import { toast } from 'react-hot-toast';
import { API_BASE_URL } from '../config.js';
import SudarshanChakraLoader from './SudarshanChakraLoader.jsx';

// Map current URL path to pipeline context ID
const getStepFromPath = (pathname) => {
  if (pathname.includes('/summary')) return 'summary';
  if (pathname.includes('/configuration')) return 'configuration';
  if (pathname.includes('/outliers')) return 'outliers';
  if (pathname.includes('/weights')) return 'weights';
  if (pathname.includes('/results')) return 'results';
  if (pathname.includes('/analytics')) return 'results';
  if (pathname.includes('/data-encryption')) return 'configuration';
  return 'upload';
};

export default function NarayanChatbot() {
  const location = useLocation();
  const currentStep = getStepFromPath(location.pathname);

  // States: closed -> intro -> chat
  const [isOpen, setIsOpen] = useState(false);
  const [viewState, setViewState] = useState('intro'); // 'intro' | 'chat'
  const [isMinimized, setIsMinimized] = useState(false);

  // Dragging state
  const [position, setPosition] = useState({ 
    x: Math.max(20, window.innerWidth - 450), 
    y: Math.max(80, window.innerHeight - 660) 
  });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "👋 **Hello! I am Narayan, your Master AI Agent for the Data Cleaning Pipeline.**\n\nI have full context over every stage of your data pipeline (Upload, Summary, Configuration, Outliers, Weights, and Results).\n\nYou can:\n• Ask me **'What is the meaning of this page?'** or **'What should I do here?'**\n• Tell me **'Remove duplicates'** or **'Encrypt phone/ID column'** and I will execute it live in Python.\n• Upload CSV/Excel files directly, or ask for **Cleaned CSV, HTML, and Black & White PDF reports**!",
      timestamp: new Date()
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [datasetInfo, setDatasetInfo] = useState({ 
    filename: 'district_health.csv', 
    rows: 35, 
    columns: 8, 
    encrypted_columns: [] 
  });
  const [stepContext, setStepContext] = useState(null);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && viewState === 'chat') {
      scrollToBottom();
    }
  }, [messages, isOpen, viewState]);

  // Handle intro state auto-transition after 1.8s
  useEffect(() => {
    let timer;
    if (isOpen && viewState === 'intro') {
      timer = setTimeout(() => {
        setViewState('chat');
      }, 1800);
    }
    return () => clearTimeout(timer);
  }, [isOpen, viewState]);

  // Fetch step context when URL changes
  useEffect(() => {
    fetchStepContext(currentStep);
  }, [currentStep, location.pathname]);

  const fetchStepContext = async (stepId) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/narayan/context/${stepId}`);
      if (res.ok) {
        const data = await res.json();
        setStepContext(data.context);
        if (data.active_dataset) {
          setDatasetInfo(data.active_dataset);
        }
      }
    } catch (e) {
      console.warn("Could not fetch step context", e);
    }
  };

  // Open Chatbot & Trigger Intro Animation
  const handleOpenChatbot = () => {
    setIsOpen(true);
    setViewState('intro');
    setIsMinimized(false);
  };

  // Dragging Handlers
  const handleMouseDown = (e) => {
    if (e.target.closest('.no-drag')) return;
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      const newX = Math.max(10, Math.min(window.innerWidth - 440, e.clientX - dragOffset.x));
      const newY = Math.max(70, Math.min(window.innerHeight - 180, e.clientY - dragOffset.y));
      setPosition({ x: newX, y: newY });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging, dragOffset]);

  // File Upload Handlers (CSV / Excel)
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/narayan/upload`, {
        method: 'POST',
        body: formData,
        credentials: 'include'
      });
      const data = await res.json();
      if (data.success) {
        setDatasetInfo({
          filename: file.name,
          rows: data.rows,
          columns: data.columns,
          encrypted_columns: []
        });
        toast.success(`Narayan received ${file.name}`);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now(),
            type: 'assistant',
            content: `✅ **Dataset Ingested into Pipeline:** \`${file.name}\`\n\n• **Records:** ${data.rows.toLocaleString()}\n• **Columns:** ${data.columns}\n• **Sample Attributes:** ${data.column_names.slice(0, 6).join(', ')}...\n\nWhat data transformations, cleaning operations, or reports would you like to run?`,
            timestamp: new Date()
          }
        ]);
      } else {
        toast.error(data.error || 'Failed to upload dataset');
      }
    } catch (err) {
      toast.error('Upload failed');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const sendQuery = async (queryText) => {
    if (!queryText.trim() || isLoading) return;
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: queryText,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/narayan/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: queryText,
          step: currentStep,
          history: messages.slice(-4).map(m => ({ role: m.type === 'user' ? 'user' : 'assistant', content: m.content }))
        }),
        credentials: 'include'
      });

      const data = await res.json();
      if (data.success) {
        if (data.dataset_info) {
          setDatasetInfo(data.dataset_info);
        }
        if (data.action_result) {
          toast.success(`Action Executed: ${data.action_executed}`);
        }

        const assistantMsg = {
          id: Date.now() + 1,
          type: 'assistant',
          content: data.response,
          actionResult: data.action_result,
          downloads: data.downloads,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, assistantMsg]);
      } else {
        setMessages(prev => [
          ...prev,
          {
            id: Date.now() + 1,
            type: 'assistant',
            content: `❌ **Notice:** ${data.error || 'Could not process command'}`,
            timestamp: new Date()
          }
        ]);
      }
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          id: Date.now() + 1,
          type: 'assistant',
          content: '❌ **Notice:** Connection to backend pipeline engine failed.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const exportDirect = async (format) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/narayan/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format })
      });
      const data = await res.json();
      if (data.success && data.download_url) {
        window.open(`${API_BASE_URL}${data.download_url}`, '_blank');
        toast.success(`Generated ${format.toUpperCase()} report!`);
      } else {
        toast.error('Failed to generate export');
      }
    } catch (e) {
      toast.error('Export failed');
    }
  };

  const formatText = (text) => {
    if (!text) return '';
    return text
      .replace(/### (.*?)\n/g, '<h3 class="text-xs font-bold text-gray-900 mt-2 mb-1">$1</h3>')
      .replace(/## (.*?)\n/g, '<h2 class="text-xs font-bold text-gray-900 mt-2 mb-1">$1</h2>')
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em class="text-gray-700 italic">$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-slate-100 border border-slate-200 px-1 py-0.5 rounded text-[11px] text-indigo-700 font-mono">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  // 1. FLOATING ACTION BUTTON (Matches Dashboard & App Design)
  if (!isOpen) {
    return (
      <div 
        style={{ 
          left: `${Math.min(position.x, window.innerWidth - 130)}px`, 
          top: `${Math.min(position.y, window.innerHeight - 80)}px` 
        }}
        className="fixed z-50 cursor-grab active:cursor-grabbing select-none"
        onMouseDown={handleMouseDown}
      >
        <button
          onClick={handleOpenChatbot}
          className="group relative flex items-center gap-2.5 bg-white hover:bg-slate-50 text-slate-800 p-2 pr-3.5 rounded-full shadow-lg border border-slate-200 hover:border-blue-300 hover:shadow-xl transition-all duration-200 cursor-pointer"
          title="Click to open Narayan - Master AI Pipeline Guide"
        >
          {/* Shiny Light Yellow Sudarshan Chakra Logo Mark */}
          <div className="w-8 h-8 rounded-full bg-amber-50/70 border border-amber-200/80 flex items-center justify-center shadow-xs">
            <SudarshanChakraLoader size={26} spinning={true} glowing={false} />
          </div>

          <div className="text-left">
            <div className="text-xs font-bold text-gray-900 flex items-center gap-1.5 tracking-tight">
              Narayan
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_6px_#10B981]" />
            </div>
            <div className="text-[10px] text-gray-500 font-normal">
              Pipeline Master
            </div>
          </div>

          {/* Clean App Blue Badge */}
          <span className="absolute -top-1.5 -right-1 bg-blue-600 text-white text-[9px] font-bold px-1.5 py-0.5 rounded-full shadow-xs">
            AI Guide
          </span>
        </button>
      </div>
    );
  }

  // 2. SUDARSHAN CHAKRA INTRO ANIMATION (Shiny Light Yellow Chakra)
  if (viewState === 'intro') {
    return (
      <div
        style={{
          left: `${position.x}px`,
          top: `${position.y}px`,
          width: '430px',
          height: '590px'
        }}
        onClick={() => setViewState('chat')}
        className="fixed z-50 bg-white/98 backdrop-blur-md rounded-2xl shadow-2xl border border-slate-200 flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-200 overflow-hidden"
      >
        {/* Soft golden-yellow radial aura */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(254,240,138,0.18)_0%,transparent_70%)] pointer-events-none" />

        {/* Center Spinning Light Yellow Shiny Sudarshan Chakra */}
        <div className="relative mb-6 transform hover:scale-105 transition-transform duration-300">
          <SudarshanChakraLoader size={145} spinning={true} glowing={true} />
        </div>

        {/* Clean Header */}
        <h2 className="text-lg font-bold text-gray-900 tracking-tight mb-1">
          Narayan
        </h2>
        
        <p className="text-xs font-semibold text-blue-600 tracking-wide mb-2">
          Pipeline Master & Data Intelligence
        </p>

        <p className="text-xs text-gray-500 max-w-xs leading-relaxed mb-6">
          Initializing pipeline context for automated cleaning, anomaly diagnostics, and audited reports...
        </p>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 border border-slate-200 text-[11px] text-slate-600">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-ping" />
          Click anywhere to skip
        </div>
      </div>
    );
  }

  // 3. RESTYLED CHATBOT INTERFACE (Matching App's Professional Theme)
  return (
    <div
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: isMinimized ? '340px' : '430px',
        height: isMinimized ? '60px' : '620px'
      }}
      className="fixed z-50 bg-white text-gray-800 rounded-2xl shadow-2xl border border-slate-200/90 flex flex-col overflow-hidden transition-all duration-150 select-none"
    >
      {/* Widget Header (Clean White / Subtle Grey) */}
      <div 
        onMouseDown={handleMouseDown}
        className="px-4 py-3 bg-white border-b border-slate-200/80 flex items-center justify-between cursor-move shadow-2xs"
      >
        <div className="flex items-center gap-2.5">
          {/* Header Chakra Logo Mark (Shiny Light Yellow) */}
          <div className="w-8 h-8 rounded-lg bg-amber-50/70 border border-amber-200/80 flex items-center justify-center shadow-xs">
            <SudarshanChakraLoader size={24} spinning={true} glowing={false} />
          </div>

          <div>
            <div className="text-xs font-bold text-gray-900 flex items-center gap-2">
              Narayan
              <span className="text-[10px] bg-blue-50 text-blue-700 border border-blue-200/60 font-semibold px-2 py-0.2 rounded-full">
                Active
              </span>
            </div>
            <div className="text-[10.5px] text-gray-500 truncate max-w-[190px]">
              Step: {stepContext?.title || currentStep}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 no-drag">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-slate-100 rounded-lg text-slate-400 hover:text-slate-600 transition cursor-pointer"
            title={isMinimized ? "Expand" : "Minimize"}
          >
            {isMinimized ? <FiMaximize2 className="w-3.5 h-3.5" /> : <FiMinimize2 className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-red-50 rounded-lg text-slate-400 hover:text-red-600 transition cursor-pointer"
            title="Close"
          >
            <FiX className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Active Dataset Bar + Upload Button */}
          <div className="px-3.5 py-2 bg-slate-50/80 border-b border-slate-200 text-xs flex items-center justify-between gap-2 text-slate-600 no-drag">
            <div className="flex items-center gap-1.5 truncate">
              <FiDatabase className="text-blue-600 flex-shrink-0" />
              <span className="font-semibold text-gray-800 truncate" title={datasetInfo.filename}>
                {datasetInfo.filename}
              </span>
              <span className="text-gray-400">({datasetInfo.rows} rows)</span>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileUpload}
              accept=".csv,.xlsx,.xls,.json"
              className="hidden"
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold text-[11px] flex items-center gap-1 cursor-pointer transition shadow-xs disabled:opacity-50"
            >
              {isUploading ? <FiRefreshCw className="animate-spin w-2.5 h-2.5" /> : <FiUpload className="w-2.5 h-2.5" />}
              Upload CSV / XL
            </button>
          </div>

          {/* Context Quick Action Pills */}
          <div className="px-3 py-1.5 bg-slate-50/50 border-b border-slate-200 overflow-x-auto flex gap-1.5 text-[11px] no-drag">
            <button
              onClick={() => sendQuery(`What is the meaning of the '${stepContext?.title || currentStep}' step and what should I do?`)}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 hover:text-blue-600 border border-slate-200 rounded-lg font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiHelpCircle className="text-blue-600 w-3 h-3" />
              Meaning of this step?
            </button>
            <button
              onClick={() => sendQuery("Remove duplicates from this dataset and show summary")}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 hover:text-blue-600 border border-slate-200 rounded-lg font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiTrash2 className="text-indigo-600 w-3 h-3" />
              Remove Duplicates
            </button>
            <button
              onClick={() => sendQuery("Encrypt sensitive columns with PBKDF2")}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 hover:text-blue-600 border border-slate-200 rounded-lg font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiLock className="text-purple-600 w-3 h-3" />
              Encrypt Columns
            </button>
            <button
              onClick={() => sendQuery("Handle outliers and winsorize at 5th percentile")}
              className="px-2.5 py-1 bg-white hover:bg-slate-50 text-slate-700 hover:text-blue-600 border border-slate-200 rounded-lg font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiZap className="text-amber-600 w-3 h-3" />
              Winsorize Outliers
            </button>
          </div>

          {/* Messages Feed */}
          <div className="flex-1 p-3.5 overflow-y-auto space-y-3.5 bg-white no-drag text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[90%] p-3.5 rounded-2xl shadow-2xs ${
                    m.type === 'user'
                      ? 'bg-blue-600 text-white rounded-br-xs'
                      : 'bg-slate-100 text-gray-800 rounded-bl-xs border border-slate-200/80'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1.5 mb-1 pb-1 border-b border-black/5 text-[10px] opacity-75 font-semibold">
                    <span>{m.type === 'user' ? 'You' : 'Narayan'}</span>
                    <span>{m.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>

                  <div
                    className="leading-relaxed text-[11.5px]"
                    dangerouslySetInnerHTML={{ __html: formatText(m.content) }}
                  />

                  {/* Transformation Action Result Box */}
                  {m.actionResult && (
                    <div className="mt-2.5 p-2 bg-emerald-50 border border-emerald-200 rounded-xl text-[11px] text-emerald-900 font-medium flex items-start gap-2">
                      <FiCheckCircle className="text-emerald-600 w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                      <span>{m.actionResult.message}</span>
                    </div>
                  )}

                  {/* Report Downloads in Chat */}
                  {m.downloads && m.downloads.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-200 flex flex-wrap gap-1.5">
                      {m.downloads.map((d, idx) => (
                        <a
                          key={idx}
                          href={`${API_BASE_URL}${d.download_url}`}
                          download={d.filename}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2.5 py-1 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-[10.5px] font-semibold flex items-center gap-1 shadow-xs transition"
                        >
                          <FiDownload className="w-3 h-3" />
                          Download {d.format?.toUpperCase()}
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-[11px] text-slate-600 flex items-center gap-2">
                  <FiRefreshCw className="animate-spin text-blue-600 w-3.5 h-3.5" />
                  <span>Narayan is calculating pipeline transformations...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Export Quick Bar (CSV, HTML, B&W PDF) */}
          <div className="px-3.5 py-2 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-500 font-semibold no-drag">
            <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">Quick Export:</span>
            <div className="flex gap-1.5">
              <button
                onClick={() => exportDirect('csv')}
                className="px-2.5 py-1 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-slate-700 font-semibold shadow-2xs transition"
              >
                CSV
              </button>
              <button
                onClick={() => exportDirect('html')}
                className="px-2.5 py-1 bg-white hover:bg-slate-100 border border-slate-200 rounded-lg text-slate-700 font-semibold shadow-2xs transition"
              >
                HTML
              </button>
              <button
                onClick={() => exportDirect('pdf')}
                className="px-2.5 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold shadow-xs transition"
              >
                B&W PDF
              </button>
            </div>
          </div>

          {/* User Chat Input Box */}
          <div className="p-3 bg-white border-t border-slate-200 no-drag">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    sendQuery(inputMessage);
                  }
                }}
                placeholder="Ask Narayan (e.g. 'remove duplicates', 'what to do here')..."
                disabled={isLoading}
                className="flex-1 text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-300 rounded-xl text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:bg-white transition"
              />
              <button
                onClick={() => sendQuery(inputMessage)}
                disabled={!inputMessage.trim() || isLoading}
                className="px-3.5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-xs cursor-pointer disabled:opacity-40 transition font-semibold flex items-center justify-center"
              >
                <FiSend className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
