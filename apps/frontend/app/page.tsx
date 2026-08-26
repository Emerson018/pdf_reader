'use client';

import React, { useState } from 'react';
import { ChatComponent } from '../components/Chat';
import { DatabaseViewerComponent } from '../components/DatabaseViewerComponent';
import { MessageSquare, Database, Sparkles, FileUp } from 'lucide-react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'database'>('chat');

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar with Tabs */}
      <nav className="bg-slate-900/90 border-b border-slate-800 px-6 py-3 sticky top-0 z-40 backdrop-blur shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-gradient-to-tr from-blue-600 via-indigo-600 to-purple-600 rounded-xl text-white shadow-md">
              <Sparkles className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <span className="text-sm font-extrabold text-slate-100 tracking-tight block">
                AI Platform Multimodal
              </span>
              <span className="text-[10px] text-slate-400">RAG • Gemini Vision • pgvector</span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-2 bg-slate-950 p-1.5 rounded-2xl border border-slate-800 shadow-inner">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 text-xs font-bold px-4 py-2 rounded-xl transition-all ${
                activeTab === 'chat'
                  ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Chatbot & Upload PDF</span>
            </button>

            <button
              onClick={() => setActiveTab('database')}
              className={`flex items-center space-x-2 text-xs font-bold px-4 py-2 rounded-xl transition-all ${
                activeTab === 'database'
                  ? 'bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
              }`}
            >
              <Database className="w-4 h-4" />
              <span>Visualizar Banco de Dados</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Tab Content */}
      <div className="flex-1">
        {activeTab === 'chat' ? (
          <ChatComponent />
        ) : (
          <DatabaseViewerComponent />
        )}
      </div>
    </main>
  );
}
