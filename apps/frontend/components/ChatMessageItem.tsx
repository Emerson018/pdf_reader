'use client';

import React, { useState } from 'react';
import { ChatMessage, exportRagReport } from '../services/api';
import { Bot, User, Sparkles, FileText, CheckCircle2, Zap, Download, FileCode } from 'lucide-react';

interface Props {
  message: ChatMessage;
}

export const ChatMessageItem: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const isCacheHit = message.metadata?.cache_hit === true;
  const cacheLatency = message.metadata?.cache_latency_ms;
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async (format: 'markdown' | 'pdf') => {
    setIsExporting(true);
    try {
      await exportRagReport(message.content, message.metadata, format);
    } catch (err: any) {
      alert(`Erro ao exportar relatório: ${err.message || err}`);
    } finally {
      setIsExporting(false);
    }
  };

  // Format content to render bold text, lists, and multi-agent headers nicely
  const renderFormattedContent = (text: string) => {
    const lines = text.split('\n');
    return lines.map((line, lineIdx) => {
      // Parse **bold** tags
      const parts = line.split(/(\*\*.*?\*\*)/g);
      const formattedLine = parts.map((part, partIdx) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return (
            <strong key={partIdx} className="font-semibold text-white">
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      });

      if (line.trim().startsWith('## ')) {
        return (
          <h2 key={lineIdx} className="text-base font-bold text-white border-b border-purple-500/30 pb-2 mt-4 mb-2 flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-purple-400 flex-shrink-0" />
            <span>{line.trim().slice(3)}</span>
          </h2>
        );
      }

      if (line.trim().startsWith('### ') || line.trim().startsWith('#### ')) {
        const headerText = line.trim().replace(/^#{3,4}\s+/, '');
        return (
          <h3 key={lineIdx} className="text-xs font-bold tracking-wide text-purple-300 bg-purple-950/60 px-3 py-2 rounded-lg border border-purple-800/50 mt-3 mb-1">
            {headerText}
          </h3>
        );
      }

      if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
        return (
          <li key={lineIdx} className="ml-4 list-disc text-slate-200 my-0.5">
            {formattedLine}
          </li>
        );
      }

      if (/^\d+\./.test(line.trim())) {
        return (
          <div key={lineIdx} className="flex items-start space-x-2 my-1 pl-2 bg-slate-900/40 p-2 rounded-lg border border-slate-800/60">
            <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5" />
            <span className="text-slate-200">{formattedLine}</span>
          </div>
        );
      }

      return (
        <p key={lineIdx} className={line.trim() === '' ? 'h-2' : 'my-1'}>
          {formattedLine}
        </p>
      );
    });
  };

  return (
    <div
      className={`flex items-start space-x-3 p-4 rounded-2xl transition-all duration-300 ${
        isUser
          ? 'bg-gradient-to-r from-blue-600/30 to-indigo-600/20 border border-blue-500/40 ml-auto max-w-[85%] shadow-md'
          : 'bg-slate-900/90 border border-slate-800/80 mr-auto max-w-[95%] shadow-lg'
      }`}
    >
      <div
        className={`flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center shadow-md ${
          isUser
            ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white'
            : 'bg-gradient-to-br from-purple-600 to-pink-600 text-white'
        }`}
      >
        {isUser ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
      </div>

      <div className="flex-1 overflow-hidden">
        <div className="flex items-center justify-between mb-1.5 border-b border-slate-800/50 pb-1">
          <div className="flex items-center space-x-2">
            <span className="text-xs font-bold tracking-wide text-slate-300">
              {isUser ? 'Você' : 'Orquestrador Multi-Agentes IA'}
            </span>
            {!isUser && (
              <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-purple-950/80 text-purple-300 px-2 py-0.5 rounded-full border border-purple-800/50">
                <FileText className="w-3 h-3 text-purple-400" /> RAG Multimodal
              </span>
            )}
            {!isUser && isCacheHit && (
              <span className="inline-flex items-center gap-1 text-[10px] font-extrabold bg-amber-950/90 text-amber-300 px-2 py-0.5 rounded-full border border-amber-500/50 shadow-sm animate-pulse">
                <Zap className="w-3 h-3 text-amber-400" />
                Redis Cache Hit ({cacheLatency || '< 5'}ms)
              </span>
            )}
          </div>
          <span className="text-[10px] font-mono text-slate-500">{message.timestamp}</span>
        </div>

        <div className="text-sm text-slate-200 leading-relaxed font-sans space-y-1">
          {renderFormattedContent(message.content)}
        </div>

        {/* Footer Action Buttons for Assistant Messages */}
        {!isUser && (
          <div className="mt-3 pt-2 border-t border-slate-800/60 flex items-center justify-end space-x-2">
            <span className="text-[10px] text-slate-500 font-medium mr-1">Exportar Relatório:</span>
            <button
              onClick={() => handleExport('markdown')}
              disabled={isExporting}
              className="inline-flex items-center gap-1 text-[11px] font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700 transition-all shadow-sm"
              title="Baixar Relatório em Markdown (.md)"
            >
              <FileCode className="w-3.5 h-3.5 text-blue-400" /> Markdown (.md)
            </button>
            <button
              onClick={() => handleExport('pdf')}
              disabled={isExporting}
              className="inline-flex items-center gap-1 text-[11px] font-semibold bg-purple-950/80 hover:bg-purple-900 text-purple-200 px-2.5 py-1 rounded-lg border border-purple-800 transition-all shadow-sm"
              title="Baixar Relatório em PDF (.pdf)"
            >
              <Download className="w-3.5 h-3.5 text-purple-400" /> PDF (.pdf)
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
