'use client';

import React from 'react';
import { ChatMessage } from '../services/api';
import { Bot, User, Sparkles, FileText, CheckCircle2 } from 'lucide-react';

interface Props {
  message: ChatMessage;
}

export const ChatMessageItem: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';

  // Format content to render bold text and lists nicely
  const renderFormattedContent = (text: str) => {
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
          : 'bg-slate-900/90 border border-slate-800/80 mr-auto max-w-[90%] shadow-lg'
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
              {isUser ? 'Você' : 'Assistente IA Platform'}
            </span>
            {!isUser && (
              <span className="inline-flex items-center gap-1 text-[10px] font-medium bg-purple-950/80 text-purple-300 px-2 py-0.5 rounded-full border border-purple-800/50">
                <FileText className="w-3 h-3 text-purple-400" /> RAG Multimodal
              </span>
            )}
          </div>
          <span className="text-[10px] font-mono text-slate-500">{message.timestamp}</span>
        </div>

        <div className="text-sm text-slate-200 leading-relaxed font-sans space-y-1">
          {renderFormattedContent(message.content)}
        </div>
      </div>
    </div>
  );
};
