'use client';

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage, uploadPdfDocument, getUploadStatus, ChatMessage, UploadStatusResponse } from '../services/api';
import { ChatMessageItem } from './ChatMessageItem';
import { UploadProgressModal } from './UploadProgressModal';
import { Send, Loader2, AlertCircle, Sparkles, Trash2, Layers, Paperclip, FileUp, CheckCircle2, Zap, Eye } from 'lucide-react';

const SUGGESTIONS = [
  'Quais são as 7 metas de segurança que estão representadas neste documento?',
  'De acordo com o documento, quais são os 5 momentos para a higienização das mãos?',
  'Quais são as diretrizes para concessão de férias no manual do colaborador?'
];

export const ChatComponent: React.FC = () => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<string | undefined>(undefined);

  // Ingestion Mode Option: processImages = true (Texto + Visão AI) vs false (Apenas Texto - Super Rápido)
  const [processImages, setProcessImages] = useState<boolean>(true);

  // Upload & Progress State
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [uploadStatus, setUploadStatus] = useState<UploadStatusResponse | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Polling hook for upload progress & ETA
  useEffect(() => {
    if (!activeTaskId) return;

    const interval = setInterval(async () => {
      try {
        const status = await getUploadStatus(activeTaskId);
        setUploadStatus(status);

        if (status.status === 'completed' || status.status === 'failed') {
          clearInterval(interval);
          if (status.status === 'completed') {
            const modeDesc = processImages ? 'Texto + Visão AI Gemini' : 'Apenas Texto (Modo Rápido)';
            const sysMsg: ChatMessage = {
              id: Date.now().toString(),
              role: 'assistant',
              content: `📄 **Documento Embeedado com Sucesso!**\nO PDF **"${status.filename}"** foi processado (${status.total_pages} páginas em Modo: **${modeDesc}**). Todos os vetores e chunks já estão salvos no PostgreSQL com pgvector! Você já pode fazer perguntas sobre ele.`,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            };
            setMessages((prev) => [...prev, sysMsg]);
          }
        }
      } catch (err: any) {
        console.error('Error fetching upload status:', err);
      }
    }, 1000);

    return () => clearInterval(interval);
  }, [activeTaskId, processImages]);

  const handleSendMessage = async (textToSend: string) => {
    if (!textToSend.trim() || isLoading) return;

    const userText = textToSend.trim();
    setInput('');
    setError(null);

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await sendChatMessage(userText, conversationId);

      if (res.conversation_id && !conversationId) {
        setConversationId(res.conversation_id);
      }

      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: res.response,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        metadata: res.metadata,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      setError(err.message || 'Falha ao enviar mensagem ao servidor.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setError('Por favor, selecione um arquivo no formato PDF.');
      return;
    }

    setError(null);
    setShowUploadModal(true);

    try {
      const res = await uploadPdfDocument(file, processImages);
      setActiveTaskId(res.task_id);
      setUploadStatus({
        task_id: res.task_id,
        filename: file.name,
        status: 'processing',
        total_pages: 0,
        current_page: 0,
        progress_percent: 0,
        elapsed_seconds: 0,
        estimated_remaining_seconds: 0,
        message: `Iniciando upload e embeeding (${processImages ? 'Texto + Visão AI' : 'Apenas Texto'})...`,
      });
    } catch (err: any) {
      setError(err.message || 'Falha ao fazer upload do PDF.');
      setShowUploadModal(false);
    } finally {
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSendMessage(input);
  };

  const handleClearChat = () => {
    setMessages([]);
    setConversationId(undefined);
    setError(null);
  };

  return (
    <div className="flex flex-col h-screen max-w-5xl mx-auto p-4 md:p-6 font-sans">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept=".pdf"
        className="hidden"
      />

      {/* Upload Progress & ETA Modal */}
      {showUploadModal && (
        <UploadProgressModal
          statusData={uploadStatus}
          onClose={() => {
            setShowUploadModal(false);
            setActiveTaskId(null);
          }}
        />
      )}

      {/* Top Header Navbar */}
      <header className="flex items-center justify-between py-3.5 px-6 bg-slate-900/90 border border-slate-800 rounded-2xl mb-4 backdrop-blur shadow-xl">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 rounded-xl text-white shadow-md">
            <Sparkles className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-extrabold text-slate-100 tracking-tight">AI Agent Platform</h1>
              <span className="bg-emerald-950 text-emerald-400 text-[10px] px-2 py-0.5 rounded-full border border-emerald-800/60 font-semibold">
                Online
              </span>
            </div>
            <p className="text-xs text-slate-400">RAG Multimodal Vision • Embeddings pgvector 768D</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Mode Selector Option Toggle: Apenas Texto vs Texto + Visão AI */}
          <div className="flex items-center space-x-1 bg-slate-950/90 p-1 rounded-xl border border-slate-800/90 shadow-inner">
            <button
              type="button"
              onClick={() => setProcessImages(false)}
              className={`flex items-center space-x-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg transition-all ${
                !processImages
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Salvar PDF extraindo APENAS TEXTO (Processamento Super Rápido)"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Apenas Texto</span>
            </button>

            <button
              type="button"
              onClick={() => setProcessImages(true)}
              className={`flex items-center space-x-1.5 text-[11px] font-bold px-3 py-1.5 rounded-lg transition-all ${
                processImages
                  ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
              title="Salvar PDF processando Texto + Visão AI Gemini de imagens/diagramas"
            >
              <Eye className="w-3.5 h-3.5 text-purple-400" />
              <span>Texto + Visão AI</span>
            </button>
          </div>

          <button
            onClick={() => fileInputRef.current?.click()}
            title="Upload de Documento PDF"
            className="flex items-center space-x-2 text-xs font-semibold text-blue-300 hover:text-white bg-blue-950/60 hover:bg-blue-900/80 px-3.5 py-2 rounded-xl border border-blue-800/60 hover:border-blue-500 transition-all shadow-md"
          >
            <FileUp className="w-4 h-4 text-blue-400" />
            <span>Enviar PDF</span>
          </button>

          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              title="Limpar Conversa"
              className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-red-400 bg-slate-800/80 hover:bg-red-950/40 px-3 py-2 rounded-xl border border-slate-700 hover:border-red-800/50 transition-all"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Limpar</span>
            </button>
          )}
        </div>
      </header>

      {/* Main Messages & Suggestions Container */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 md:p-6 bg-slate-950/70 rounded-2xl border border-slate-900 shadow-2xl backdrop-blur">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 md:p-12 text-slate-400">
            <div className="p-4 bg-gradient-to-tr from-purple-900/30 to-blue-900/30 rounded-3xl border border-purple-500/20 mb-4 shadow-lg">
              <Layers className="w-12 h-12 text-purple-400 animate-bounce" />
            </div>
            <h3 className="text-xl font-bold text-slate-200 mb-2">
              Assistente Virtual & RAG Multimodal
            </h3>
            <p className="text-sm max-w-lg text-slate-400 mb-6 leading-relaxed">
              Consulte dados de documentos PDF, infográficos visuais, normas internas e metas hospitalares processadas via **Gemini Vision** e **pgvector**.
            </p>

            {/* Ingestion Mode Badge Selection Box in Empty State */}
            <div className="flex items-center justify-center space-x-3 mb-6 bg-slate-900/90 p-2.5 rounded-2xl border border-slate-800 shadow-md">
              <span className="text-xs font-semibold text-slate-400">Modo de Upload:</span>
              <button
                type="button"
                onClick={() => setProcessImages(false)}
                className={`flex items-center space-x-1 text-xs font-bold px-3 py-1.5 rounded-xl transition-all ${
                  !processImages
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                <span>⚡ Apenas Texto (Super Rápido)</span>
              </button>
              <button
                type="button"
                onClick={() => setProcessImages(true)}
                className={`flex items-center space-x-1 text-xs font-bold px-3 py-1.5 rounded-xl transition-all ${
                  processImages
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50 shadow'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Eye className="w-3.5 h-3.5 text-purple-400" />
                <span>👁️ Texto + Visão AI (Exaustivo)</span>
              </button>
            </div>

            {/* Prominent Upload PDF Action Box */}
            <button
              onClick={() => fileInputRef.current?.click()}
              className="w-full max-w-xl mb-6 p-4 bg-gradient-to-r from-blue-950/80 via-slate-900 to-purple-950/80 hover:from-blue-900 hover:to-purple-900 border-2 border-dashed border-blue-500/40 hover:border-blue-400 rounded-2xl flex items-center justify-between text-left transition-all duration-200 group shadow-lg"
            >
              <div className="flex items-center space-x-3">
                <div className="p-3 bg-blue-600 rounded-xl text-white group-hover:scale-110 transition-transform shadow-md">
                  <FileUp className="w-6 h-6" />
                </div>
                <div>
                  <h4 className="text-sm font-bold text-slate-100">
                    Enviar PDF ({processImages ? 'Texto + Visão AI' : 'Modo Apenas Texto ⚡'})
                  </h4>
                  <p className="text-xs text-slate-400">Faça o upload para realizar o embeeding com acompanhamento do tempo restante (ETA)</p>
                </div>
              </div>
              <span className="text-xs font-semibold bg-blue-600 text-white px-3 py-1.5 rounded-xl group-hover:bg-blue-500 transition-colors shadow">
                Upload
              </span>
            </button>

            <div className="w-full max-w-xl">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3 text-left">
                Sugestões de Perguntas Rápidas:
              </p>
              <div className="grid grid-cols-1 gap-2">
                {SUGGESTIONS.map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(suggestion)}
                    className="p-3 text-xs text-left bg-slate-900/90 hover:bg-slate-800/90 border border-slate-800/80 hover:border-purple-500/40 rounded-xl text-slate-300 hover:text-white transition-all shadow-sm flex items-center justify-between group"
                  >
                    <span>{suggestion}</span>
                    <Sparkles className="w-3.5 h-3.5 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessageItem key={msg.id} message={msg} />)
        )}

        {isLoading && (
          <div className="flex items-center space-x-3 p-4 bg-slate-900/90 border border-slate-800 rounded-2xl max-w-[80%] shadow-lg">
            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
            <span className="text-xs font-medium text-slate-300">
              Buscando e processando resposta no banco de dados vetorial PostgreSQL...
            </span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Error Alert Box */}
      {error && (
        <div className="my-2 p-3 bg-red-950/80 border border-red-800 text-red-300 text-xs rounded-xl flex items-center space-x-2 shadow-lg animate-shake">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0" />
          <span className="flex-1">{error}</span>
          <button onClick={() => setError(null)} className="text-red-400 hover:text-red-200 text-xs font-bold px-1">
            ✕
          </button>
        </div>
      )}

      {/* Input Message Form */}
      <form onSubmit={handleSubmit} className="mt-4 flex items-center space-x-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Faça uma pergunta sobre o documento ou selecione um PDF..."
            disabled={isLoading}
            className="w-full pl-11 pr-4 py-3.5 bg-slate-900/90 text-slate-100 placeholder-slate-500 rounded-2xl border border-slate-800 focus:outline-none focus:border-purple-500/80 focus:ring-1 focus:ring-purple-500/80 text-sm shadow-inner transition-all disabled:opacity-50"
          />

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            title={`Enviar PDF (${processImages ? 'Texto + Visão AI' : 'Modo Apenas Texto ⚡'})`}
            className="absolute left-3 top-1/2 -translate-y-1/2 p-1.5 text-slate-400 hover:text-blue-400 bg-slate-800/80 hover:bg-blue-950/60 rounded-xl transition-all border border-slate-700/60 hover:border-blue-600/50"
          >
            <Paperclip className="w-4 h-4" />
          </button>
        </div>

        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="p-3.5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white rounded-2xl disabled:opacity-40 disabled:hover:from-blue-600 disabled:hover:to-purple-600 transition-all shadow-lg flex items-center justify-center"
        >
          {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
        </button>
      </form>
    </div>
  );
};
