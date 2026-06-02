import { useState } from 'react';
import { AlertCircle, CheckCircle2, ShieldAlert, ChevronDown, ChevronUp, RefreshCw } from 'lucide-react';
import type { RecoveryAttempt } from '../types';

interface RecoveryTimelineProps {
  attempts: RecoveryAttempt[];
}

export default function RecoveryTimeline({ attempts }: RecoveryTimelineProps) {
  const [expandedAttempts, setExpandedAttempts] = useState<Record<number, boolean>>({
    1: true // Expand the first attempt by default
  });

  if (!attempts || attempts.length === 0) {
    return null;
  }

  const toggleExpand = (attemptNum: number) => {
    setExpandedAttempts(prev => ({
      ...prev,
      [attemptNum]: !prev[attemptNum]
    }));
  };

  return (
    <div className="flex flex-col bg-[#1e1e2e]/30 border border-slate-800 rounded-xl overflow-hidden mt-6">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-3 bg-[#1e1e2e]/80 border-b border-slate-800">
        <RefreshCw className="h-4 w-4 text-amber-500 animate-spin [animation-duration:10s]" />
        <span className="text-xs font-semibold text-slate-300">AUTO-CORRECTION TIMELINE</span>
        <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded-full font-medium">
          {attempts.length} {attempts.length === 1 ? 'Attempt' : 'Attempts'}
        </span>
      </div>

      {/* Stepper Body */}
      <div className="p-4 space-y-4 bg-[#11111b]/10">
        {attempts.map((attempt, idx) => {
          const isExpanded = !!expandedAttempts[attempt.attempt_number];
          const isLast = idx === attempts.length - 1;
          
          let icon = <AlertCircle className="h-5 w-5 text-amber-500 bg-[#11111b] rounded-full shrink-0" />;
          let titleColor = "text-slate-300";
          let badgeText = "Failed";
          let badgeClass = "bg-red-500/10 text-red-400 border border-red-500/20";
          
          if (attempt.status === "success") {
            icon = <CheckCircle2 className="h-5 w-5 text-emerald-500 bg-[#11111b] rounded-full shrink-0" />;
            titleColor = "text-emerald-400 font-semibold";
            badgeText = "Succeeded";
            badgeClass = "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
          } else if (attempt.status === "blocked") {
            icon = <ShieldAlert className="h-5 w-5 text-red-500 bg-[#11111b] rounded-full shrink-0" />;
            titleColor = "text-red-400";
            badgeText = "Blocked by Safety";
            badgeClass = "bg-red-500/10 text-red-400 border border-red-500/20";
          }

          return (
            <div key={attempt.attempt_number} className="relative flex gap-3.5 items-start timeline-item">
              {/* Stepper Line Connectors */}
              {!isLast && (
                <div className="absolute left-[9px] top-6 w-0.5 h-[calc(100%+16px)] bg-slate-800" />
              )}

              {/* Status Icon */}
              <div className="z-10 mt-0.5 shrink-0">
                {icon}
              </div>

              {/* Card Container */}
              <div className="flex-1 bg-[#1e1e2e]/60 border border-slate-800/80 rounded-lg overflow-hidden transition-all duration-200">
                {/* Accordion Trigger */}
                <div
                  onClick={() => toggleExpand(attempt.attempt_number)}
                  className="flex items-center justify-between p-3 cursor-pointer hover:bg-slate-800/25 transition-colors"
                >
                  <div className="flex items-center gap-2.5">
                    <span className="text-xs font-medium text-slate-400 font-mono">
                      Step {attempt.attempt_number}
                    </span>
                    <span className={`text-xs ${titleColor}`}>
                      {attempt.status === "success" 
                        ? "Query Auto-Corrected Successfully" 
                        : "Query Correction Attempted"}
                    </span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${badgeClass}`}>
                      {badgeText}
                    </span>
                  </div>
                  
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4 text-slate-500" />
                  ) : (
                    <ChevronDown className="h-4 w-4 text-slate-500" />
                  )}
                </div>

                {/* Collapsible Details */}
                {isExpanded && (
                  <div className="p-3 border-t border-slate-800/80 bg-[#11111b]/20 space-y-3">
                    {/* Failed SQL Codeblock */}
                    <div>
                      <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 font-mono">
                        Failed SQL
                      </div>
                      <pre className="p-2.5 bg-[#11111b] border border-slate-800/60 rounded font-mono text-[11px] text-red-300/80 overflow-x-auto whitespace-pre-wrap max-h-[120px]">
                        {attempt.failed_sql}
                      </pre>
                    </div>

                    {/* DuckDB Error Message */}
                    <div>
                      <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 font-mono">
                        DuckDB Error Received
                      </div>
                      <p className="p-2.5 bg-red-950/10 border border-red-950/20 text-red-400 rounded font-mono text-[11px] break-all whitespace-pre-wrap">
                        {attempt.error_message}
                      </p>
                    </div>

                    {/* Corrected SQL Output */}
                    {attempt.corrected_sql && (
                      <div>
                        <div className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider mb-1.5 font-mono">
                          Corrected SQL Generated
                        </div>
                        <pre className="p-2.5 bg-[#11111b] border border-slate-800/60 rounded font-mono text-[11px] text-emerald-300/80 overflow-x-auto whitespace-pre-wrap max-h-[120px]">
                          {attempt.corrected_sql}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
