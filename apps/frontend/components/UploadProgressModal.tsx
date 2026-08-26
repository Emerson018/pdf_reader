'use client';

import React from 'react';
import { UploadStatusResponse } from '../services/api';
import { FileText, Loader2, CheckCircle2, XCircle, Clock, Database, Sparkles, X } from 'lucide-react';

interface UploadProgressModalProps {
  statusData: UploadStatusResponse | null;
  onClose: () => void;
}

export const UploadProgressModal: React.FC<UploadProgressModalProps> = ({ statusData, onClose }) => {
  if (!statusData) return null;

  const isCompleted = statusData.status === 'completed';
  const isFailed = statusData.status === 'failed';
  const isProcessing = statusData.status === 'processing';

  const formatTime = (seconds: number) => {
    if (seconds <= 0) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    if (mins > 0) {
      return `${mins}m ${secs}s`;
    }
    return `${secs}s`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl relative overflow-hidden">
        {/* Decorative Top Gradient Glow */}
        <div className="absolute -top-12 -left-12 w-36 h-36 bg-blue-600/20 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute -bottom-12 -right-12 w-36 h-36 bg-purple-600/20 rounded-full blur-3xl pointer-events-none" />

        {/* Modal Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-blue-950/80 border border-blue-800/60 rounded-2xl text-blue-400">
              <FileText className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100 line-clamp-1">{statusData.filename}</h3>
              <p className="text-xs text-slate-400">Ingestão & Embedding no Banco de Dados</p>
            </div>
          </div>
          {(isCompleted || isFailed) && (
            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-xl transition-all"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Dynamic Status Icon & Message */}
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs font-semibold">
            <span className="flex items-center space-x-2 text-slate-300">
              {isProcessing && <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />}
              {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
              {isFailed && <XCircle className="w-4 h-4 text-red-400" />}
              <span>{statusData.message}</span>
            </span>
            <span className="text-blue-400 font-mono font-bold text-sm">
              {statusData.progress_percent}%
            </span>
          </div>

          {/* Animated Gradient Progress Bar */}
          <div className="w-full bg-slate-950 rounded-full h-3.5 p-0.5 border border-slate-800 overflow-hidden shadow-inner">
            <div
              className={`h-full rounded-full transition-all duration-300 ${
                isCompleted
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-400'
                  : isFailed
                  ? 'bg-red-500'
                  : 'bg-gradient-to-r from-blue-600 via-indigo-500 to-purple-600 animate-pulse'
              }`}
              style={{ width: `${Math.min(100, Math.max(2, statusData.progress_percent))}%` }}
            />
          </div>

          {/* Page Counter & Time Tracker Grid */}
          <div className="grid grid-cols-2 gap-3 pt-2">
            <div className="bg-slate-950/70 p-3 rounded-2xl border border-slate-800/80 flex items-center space-x-3">
              <Database className="w-4 h-4 text-indigo-400 flex-shrink-0" />
              <div>
                <span className="text-[10px] text-slate-500 font-medium block">Páginas Lidas</span>
                <span className="text-xs font-bold text-slate-200">
                  {statusData.total_pages > 0 ? `${statusData.current_page} / ${statusData.total_pages}` : 'Lendo PDF...'}
                </span>
              </div>
            </div>

            <div className="bg-slate-950/70 p-3 rounded-2xl border border-slate-800/80 flex items-center space-x-3">
              <Clock className="w-4 h-4 text-purple-400 flex-shrink-0" />
              <div>
                <span className="text-[10px] text-slate-500 font-medium block">Tempo Restante (ETA)</span>
                <span className="text-xs font-bold text-purple-300 font-mono">
                  {isProcessing ? formatTime(statusData.estimated_remaining_seconds) : isCompleted ? 'Concluído' : '0s'}
                </span>
              </div>
            </div>
          </div>

          {/* Footer Info */}
          <div className="flex items-center justify-between text-[11px] text-slate-500 px-1 pt-1">
            <span>Tempo Decorrido: <strong className="text-slate-400 font-mono">{formatTime(statusData.elapsed_seconds)}</strong></span>
            <span className="flex items-center space-x-1">
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>pgvector + Gemini Vision</span>
            </span>
          </div>

          {/* Close Action Button when finished */}
          {(isCompleted || isFailed) && (
            <button
              onClick={onClose}
              className={`w-full py-3 mt-2 rounded-2xl font-bold text-xs text-white transition-all shadow-lg ${
                isCompleted
                  ? 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500'
                  : 'bg-slate-800 hover:bg-slate-700 text-slate-200'
              }`}
            >
              {isCompleted ? 'Concluído! Iniciar Perguntas' : 'Fechar'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
