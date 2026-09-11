import React, { useState, useRef, useEffect } from 'react';
import { 
  FiUpload, 
  FiSend, 
  FiDownload, 
  FiDatabase, 
  FiFileText, 
  FiRefreshCw, 
  FiInfo, 
  FiLock, 
  FiTrash2, 
  FiHelpCircle,
  FiMinimize2,
  FiMaximize2,
  FiMove,
  FiCheckCircle,
  FiZap,
  FiX,
  FiCheck
} from 'react-icons/fi';
import { BsRobot, BsLightningChargeFill, BsCpu } from 'react-icons/bs';
import { HiSparkles } from 'react-icons/hi';
import { toast } from 'react-hot-toast';
import { API_BASE_URL } from '../config.js';

export default function NarayanAssistant({ currentStep = 'upload' }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [position, setPosition] = useState({ x: window.innerWidth - 440, y: window.innerHeight - 620 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: "👋 Namaste! I am **Narayan**, your **Master AI Agent for the Data Cleaning Pipeline**.\n\nI possess complete mastery over every stage of this pipeline (Upload, Summary, Configuration, Outliers, Weights, Results). You can:\n• Ask me **'What is the meaning of this page?'** or **'What should I do here?'**\n• Tell me **'Remove duplicates'** or **'Encrypt phone/ID column'** and I will execute it in Python.\n• Upload CSV/Excel files directly or ask for **Cleaned CSV, HTML, and Black & White PDF reports**!",
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [datasetInfo, setDatasetInfo] = useState({ filename: 'district_health.csv', rows: 35, columns: 8, encrypted_columns: [] });
  const [stepContext, setStepContext] = useState(null);

  const fileInputRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, isOpen]);

  // Fetch step context when currentStep changes
  useEffect(() => {
    fetchStepContext(currentStep);
  }, [currentStep]);

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

  // Draggable logic
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
      const newX = Math.max(10, Math.min(window.innerWidth - 420, e.clientX - dragOffset.x));
      const newY = Math.max(70, Math.min(window.innerHeight - 200, e.clientY - dragOffset.y));
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
        toast.success(`Narayan ingested ${file.name}`);
        setMessages(prev => [
          ...prev,
          {
            id: Date.now(),
            type: 'assistant',
            content: `✅ **Dataset Uploaded into Narayan Workspace:** \`${file.name}\`\n\n• **Rows:** ${data.rows.toLocaleString()}\n• **Columns:** ${data.columns}\n• **Attributes:** ${data.column_names.slice(0, 6).join(', ')}...\n\nWhat pipeline transformations would you like to perform on this data?`,
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
          toast.success(`Executed: ${data.action_executed}`);
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
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 py-0.5 rounded text-[11px] text-indigo-700 font-mono">$1</code>')
      .replace(/\n/g, '<br/>');
  };

  // Floating Minimized Icon
  if (!isOpen) {
    return (
      <div 
        style={{ left: `${Math.min(position.x, window.innerWidth - 120)}px`, top: `${Math.min(position.y, window.innerHeight - 80)}px` }}
        className="fixed z-50 cursor-grab active:cursor-grabbing select-none"
        onMouseDown={handleMouseDown}
      >
        <button
          onClick={() => { setIsOpen(true); setIsMinimized(false); }}
          className="group relative flex items-center gap-2 bg-gradient-to-r from-blue-700 via-indigo-700 to-purple-800 hover:from-blue-800 hover:to-purple-900 text-white p-2.5 pr-4 rounded-full shadow-2xl border-2 border-white/80 hover:scale-105 transition-all duration-200 cursor-pointer"
          title="Click to open Narayan - Master AI Pipeline Guide"
        >
          <div className="w-9 h-9 rounded-full bg-white/20 flex items-center justify-center text-white text-lg font-bold">
            <BsRobot className="w-5 h-5 animate-bounce" />
          </div>
          <div className="text-left">
            <div className="text-xs font-bold flex items-center gap-1">
              Narayan
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            </div>
            <div className="text-[10px] text-blue-200 font-medium">Pipeline Master</div>
          </div>
          <span className="absolute -top-1 -right-1 bg-amber-400 text-slate-900 text-[9px] font-black px-1.5 py-0.5 rounded-full uppercase tracking-tighter shadow-sm">
            AI Guide
          </span>
        </button>
      </div>
    );
  }

  // Floating Expanded / Minimized Widget
  return (
    <div
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`,
        width: isMinimized ? '320px' : '420px',
        height: isMinimized ? '58px' : '580px'
      }}
      className="fixed z-50 bg-white rounded-2xl shadow-2xl border border-slate-300 flex flex-col overflow-hidden transition-all duration-150 animate-in fade-in select-none"
    >
      {/* Widget Header (Draggable) */}
      <div 
        onMouseDown={handleMouseDown}
        className="p-3 bg-gradient-to-r from-blue-800 via-indigo-800 to-slate-900 text-white flex items-center justify-between cursor-move"
      >
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-white/15 flex items-center justify-center text-white">
            <BsRobot className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold flex items-center gap-1.5">
              Narayan - Pipeline Master
              <span className="text-[9px] bg-emerald-500/30 text-emerald-300 border border-emerald-400/40 px-1.5 py-0.2 rounded font-medium">
                Live
              </span>
            </div>
            <div className="text-[10px] text-blue-200 truncate max-w-[180px]">
              Step: {stepContext?.title || currentStep}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1 no-drag">
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-white/20 rounded text-slate-200 hover:text-white transition cursor-pointer"
            title={isMinimized ? "Expand" : "Minimize"}
          >
            {isMinimized ? <FiMaximize2 className="w-3.5 h-3.5" /> : <FiMinimize2 className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setIsOpen(false)}
            className="p-1 hover:bg-red-500/40 rounded text-slate-200 hover:text-white transition cursor-pointer"
            title="Close"
          >
            <FiX className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Quick Context & Actions Bar */}
          <div className="px-3 py-2 bg-slate-100/90 border-b border-slate-200 text-[11px] flex items-center justify-between gap-2 no-drag">
            <div className="flex items-center gap-1 text-slate-700 truncate">
              <FiDatabase className="text-blue-600 flex-shrink-0" />
              <span className="font-semibold truncate" title={datasetInfo.filename}>
                {datasetInfo.filename}
              </span>
              <span className="text-slate-400">({datasetInfo.rows} rows)</span>
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
              className="px-2 py-0.5 bg-white border border-slate-300 hover:bg-slate-50 text-slate-800 rounded font-semibold text-[10px] flex items-center gap-1 cursor-pointer transition shadow-2xs"
            >
              {isUploading ? <FiRefreshCw className="animate-spin w-2.5 h-2.5" /> : <FiUpload className="w-2.5 h-2.5 text-blue-600" />}
              Upload
            </button>
          </div>

          {/* Quick Prompt Pills for this pipeline step */}
          <div className="px-3 py-1.5 bg-slate-50 border-b border-slate-200 overflow-x-auto flex gap-1.5 text-[10px] no-drag">
            <button
              onClick={() => sendQuery(`What is the meaning of the '${stepContext?.title || currentStep}' step and what should I do?`)}
              className="px-2 py-1 bg-white hover:bg-blue-50 hover:text-blue-700 text-slate-700 border border-slate-200 rounded-md font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiHelpCircle className="text-blue-600 w-3 h-3" />
              Meaning of this step?
            </button>
            <button
              onClick={() => sendQuery("Remove duplicates from this dataset and show summary")}
              className="px-2 py-1 bg-white hover:bg-indigo-50 hover:text-indigo-700 text-slate-700 border border-slate-200 rounded-md font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiTrash2 className="text-indigo-600 w-3 h-3" />
              Remove Duplicates
            </button>
            <button
              onClick={() => sendQuery("Encrypt sensitive columns with PBKDF2")}
              className="px-2 py-1 bg-white hover:bg-purple-50 hover:text-purple-700 text-slate-700 border border-slate-200 rounded-md font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiLock className="text-purple-600 w-3 h-3" />
              Encrypt Columns
            </button>
            <button
              onClick={() => sendQuery("Handle outliers and winsorize at 5th percentile")}
              className="px-2 py-1 bg-white hover:bg-amber-50 hover:text-amber-700 text-slate-700 border border-slate-200 rounded-md font-medium whitespace-nowrap cursor-pointer transition flex items-center gap-1 shadow-2xs"
            >
              <FiZap className="text-amber-600 w-3 h-3" />
              Winsorize Outliers
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 p-3 overflow-y-auto space-y-3 bg-white no-drag text-xs">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex ${m.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[90%] p-3 rounded-xl shadow-2xs ${
                    m.type === 'user'
                      ? 'bg-blue-700 text-white rounded-br-xs'
                      : 'bg-slate-100 text-slate-800 rounded-bl-xs border border-slate-200'
                  }`}
                >
                  <div className="flex items-center justify-between gap-1 mb-1 pb-1 border-b border-black/5 text-[10px] opacity-75 font-semibold">
                    <span>{m.type === 'user' ? 'You' : 'Narayan (Pipeline AI)'}</span>
                    <span>{m.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                  </div>

                  <div
                    className="leading-relaxed text-[11.5px]"
                    dangerouslySetInnerHTML={{ __html: formatText(m.content) }}
                  />

                  {/* Action Banner if operation was run */}
                  {m.actionResult && (
                    <div className="mt-2 p-2 bg-emerald-50 border border-emerald-200 rounded-lg text-[10.5px] text-emerald-900 font-medium flex items-start gap-1.5">
                      <FiCheckCircle className="text-emerald-600 w-3.5 h-3.5 flex-shrink-0 mt-0.5" />
                      <span>{m.actionResult.message}</span>
                    </div>
                  )}

                  {/* Downloads if generated */}
                  {m.downloads && m.downloads.length > 0 && (
                    <div className="mt-2.5 pt-2 border-t border-slate-200 flex flex-wrap gap-1.5">
                      {m.downloads.map((d, idx) => (
                        <a
                          key={idx}
                          href={`${API_BASE_URL}${d.download_url}`}
                          download={d.filename}
                          target="_blank"
                          rel="noreferrer"
                          className="px-2 py-1 bg-black hover:bg-neutral-800 text-white rounded text-[10px] font-bold flex items-center gap-1 shadow-xs transition"
                        >
                          <FiDownload className="w-2.5 h-2.5" />
                          {d.format?.toUpperCase()} Output
                        </a>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="p-2.5 bg-slate-100 border border-slate-200 rounded-xl text-[11px] text-slate-600 flex items-center gap-2">
                  <FiRefreshCw className="animate-spin text-blue-600 w-3.5 h-3.5" />
                  <span>Narayan is computing pipeline transformations...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Export Toolbar */}
          <div className="px-3 py-1.5 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-[10px] no-drag">
            <span className="text-slate-400 font-bold uppercase tracking-wider">Quick Export:</span>
            <div className="flex gap-1">
              <button
                onClick={() => exportDirect('csv')}
                className="px-2 py-0.5 bg-white hover:bg-slate-100 border border-slate-300 rounded font-bold text-slate-700 cursor-pointer shadow-2xs"
              >
                CSV
              </button>
              <button
                onClick={() => exportDirect('html')}
                className="px-2 py-0.5 bg-white hover:bg-slate-100 border border-slate-300 rounded font-bold text-slate-700 cursor-pointer shadow-2xs"
              >
                HTML
              </button>
              <button
                onClick={() => exportDirect('pdf')}
                className="px-2 py-0.5 bg-black hover:bg-neutral-800 text-white rounded font-bold cursor-pointer shadow-2xs"
              >
                B&W PDF
              </button>
            </div>
          </div>

          {/* Input Box */}
          <div className="p-2.5 bg-white border-t border-slate-200 no-drag">
            <div className="flex gap-1.5">
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
                className="flex-1 text-xs px-3 py-2 border border-slate-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-600 bg-slate-50"
              />
              <button
                onClick={() => sendQuery(inputMessage)}
                disabled={!inputMessage.trim() || isLoading}
                className="p-2 bg-gradient-to-r from-blue-700 to-indigo-800 hover:from-blue-800 hover:to-indigo-900 text-white rounded-xl shadow cursor-pointer disabled:opacity-40"
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
