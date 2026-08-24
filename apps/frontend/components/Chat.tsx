'use client';

import React, { useState, useRef, useEffect } from 'react';
import { sendChatMessage, ChatMessage } from '../services/api';
import { ChatMessageItem } from './ChatMessageItem';
import { Send, Loader2, AlertCircle, Sparkles, Trash2, ShieldCheck, FileCheck, Layers } from 'lucide-react';

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

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (textToSend: str) => {
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
      {/* Top Header Navbar */}
      <header className="flex items-center justify-between py-4 px-6 bg-slate-900/90 border border-slate-800 rounded-2xl mb-4 backdrop-blur shadow-xl">
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
            <p className="text-xs text-slate-400">RAG Multimodal Vision • Orquestração de Agentes Especialistas</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {messages.length > 0 && (
            <button
              onClick={handleClearChat}
              title="Limpar Conversa"
              className="flex items-center space-x-1.5 text-xs text-slate-400 hover:text-red-400 bg-slate-800/80 hover:bg-red-950/40 px-3 py-1.5 rounded-xl border border-slate-700 hover:border-red-800/50 transition-all"
            >
              <Trash2 className="w-4 h-4" />
              <span className="hidden sm:inline">Limpar</span>
            </button>
          )}

          {conversationId && (
            <span className="text-[11px] bg-slate-800/90 text-slate-300 px-3 py-1 rounded-xl border border-slate-700 font-mono shadow-inner">
              Sessão: {conversationId.slice(0, 8)}
            </span>
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
              Consulte dados do **Manual do Colaborador**, infográficos visuais, normas internas e metas hospitalares processadas via **Gemini Vision** e **pgvector**.
            </p>

            {/* Quick Suggestion Chips */}
            <div className="w-full max-w-xl space-y-2 text-left">
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                Perguntas Frequentes Sugeridas:
              </span>
              {SUGGESTIONS.map((sug, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(sug)}
                  className="w-full p-3 bg-slate-900/80 hover:bg-slate-800 text-slate-300 hover:text-white rounded-xl border border-slate-800 hover:border-blue-500/50 text-xs text-left transition-all duration-200 flex items-center justify-between group shadow-sm"
                >
                  <span className="line-clamp-1">{sug}</span>
                  <Send className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 text-blue-400 transition-opacity flex-shrink-0 ml-2" />
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((msg) => <ChatMessageItem key={msg.id} message={msg} />)
        )}

        {isLoading && (
          <div className="flex items-center space-x-3 p-4 bg-slate-900/60 border border-slate-800 rounded-2xl text-slate-300 text-sm animate-pulse max-w-[70%] shadow">
            <Loader2 className="w-5 h-5 animate-spin text-purple-400 flex-shrink-0" />
            <span>Consultando RAG Multimodal e Orquestrador...</span>
          </div>
        )}

        {error && (
          <div className="flex items-center space-x-3 p-4 bg-red-950/40 border border-red-800/60 rounded-2xl text-red-300 text-sm shadow">
            <AlertCircle className="w-5 h-5 flex-shrink-0 text-red-400" />
            <span>{error}</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="flex items-center bg-slate-900/90 border border-slate-800/90 rounded-2xl p-2 focus-within:border-blue-500 transition-all duration-200 shadow-xl backdrop-blur">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Digite sua pergunta sobre o documento, normas ou imagens..."
            disabled={isLoading}
            className="flex-1 bg-transparent px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none disabled:opacity-50 font-sans"
          />
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-600 text-white rounded-xl transition-all shadow-md focus:outline-none flex items-center justify-center"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
