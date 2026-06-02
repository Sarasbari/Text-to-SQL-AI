import { History, Trash2, CheckCircle, XCircle } from 'lucide-react';
import type { GenerateResponse } from '../types';

interface HistoryPanelProps {
  history: GenerateResponse[];
  onSelectHistory: (item: GenerateResponse) => void;
  onClearHistory: () => void;
  activeId: string | null;
}

export default function HistoryPanel({
  history,
  onSelectHistory,
  onClearHistory,
  activeId
}: HistoryPanelProps) {
  return (
    <div className="flex flex-col h-full bg-[#1e1e2e]/50 border border-slate-800 rounded-xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-[#1e1e2e]/80">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-200 text-sm">Query History</h3>
        </div>
        {history.length > 0 && (
          <button
            onClick={onClearHistory}
            className="text-slate-500 hover:text-red-400 p-1.5 rounded-lg hover:bg-red-500/10 transition-colors"
            title="Clear all query history"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* History Items List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {history.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 px-4 text-center text-slate-500">
            <History className="h-8 w-8 text-slate-700 mb-2" />
            <p className="text-xs">No questions asked yet.</p>
            <span className="text-[10px] text-slate-600 mt-1">Queries you run in this session will show up here</span>
          </div>
        ) : (
          history.map((item) => {
            const isActive = activeId === item.request_id;
            const isSuccess = item.status === "success";
            
            return (
              <div
                key={item.request_id}
                onClick={() => onSelectHistory(item)}
                className={`group flex flex-col p-3 rounded-lg cursor-pointer border text-left transition-all ${
                  isActive
                    ? 'bg-indigo-600/15 border-indigo-500/50 shadow-md shadow-indigo-950/20'
                    : 'bg-[#1e1e2e]/30 border-slate-800/80 hover:bg-slate-800/30 hover:border-slate-700/80'
                }`}
              >
                {/* Question */}
                <p className={`text-xs font-medium truncate ${
                  isActive ? 'text-indigo-200' : 'text-slate-300'
                }`}>
                  {item.question}
                </p>

                {/* Meta details */}
                <div className="flex items-center justify-between mt-2.5">
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
                    {isSuccess ? (
                      <CheckCircle className="h-3.5 w-3.5 text-emerald-500" />
                    ) : (
                      <XCircle className="h-3.5 w-3.5 text-red-500" />
                    )}
                    <span>
                      {isSuccess ? 'Success' : 'Error'}
                    </span>
                    {item.recovery && item.recovery.length > 0 && (
                      <span className="bg-amber-500/10 text-amber-400 px-1 py-0.2 rounded font-medium border border-amber-500/10">
                        {item.recovery.length} {item.recovery.length === 1 ? 'retry' : 'retries'}
                      </span>
                    )}
                  </div>

                  <span className="text-[9px] text-slate-500 font-mono">
                    {item.timings.total_ms}ms
                  </span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
