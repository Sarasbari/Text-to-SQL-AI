import { useState } from 'react';
import Editor from '@monaco-editor/react';
import type { Monaco } from '@monaco-editor/react';
import { Play, RotateCcw, Copy, Check } from 'lucide-react';

interface MonacoSqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  onExecute: () => void;
  onReset: () => void;
  isExecuting: boolean;
  hasChanges: boolean;
}

export default function MonacoSqlEditor({
  value,
  onChange,
  onExecute,
  onReset,
  isExecuting,
  hasChanges
}: MonacoSqlEditorProps) {
  const [copied, setCopied] = useState(false);

  const handleEditorDidMount = (editor: any, monaco: Monaco) => {
    // Register keyboard shortcut Ctrl+Enter or Cmd+Enter to execute SQL
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onExecute();
    });
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const editorOptions = {
    minimap: { enabled: false },
    fontSize: 13,
    fontFamily: "'Fira Code', 'Courier New', Courier, monospace",
    lineHeight: 20,
    automaticLayout: true,
    scrollBeyondLastLine: false,
    tabSize: 4,
    wordWrap: 'on' as const,
    padding: { top: 12, bottom: 12 }
  };

  return (
    <div className="flex flex-col h-full bg-[#1e1e2e]/30 border border-slate-800 rounded-xl overflow-hidden">
      {/* Editor Header Toolbar */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1e1e2e]/80 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold text-slate-300">SQL EDITOR</span>
          {hasChanges && (
            <span className="text-[10px] bg-indigo-950 text-indigo-300 border border-indigo-800 px-2 py-0.5 rounded-full font-medium">
              Modified
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {/* Copy Button */}
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800/80 transition-colors"
            title="Copy SQL to clipboard"
          >
            {copied ? (
              <>
                <Check className="h-3.5 w-3.5 text-emerald-400" />
                <span className="text-emerald-400">Copied</span>
              </>
            ) : (
              <>
                <Copy className="h-3.5 w-3.5" />
                <span>Copy</span>
              </>
            )}
          </button>

          {/* Reset Button */}
          {hasChanges && (
            <button
              onClick={onReset}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800/80 transition-colors"
              title="Reset to generated query"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              <span>Reset</span>
            </button>
          )}

          {/* Run Button */}
          <button
            onClick={onExecute}
            disabled={isExecuting || !value.trim()}
            className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-500 text-white shadow-lg shadow-indigo-900/20 hover:shadow-indigo-900/40 transition-all cursor-pointer"
            title="Run Query (Ctrl + Enter)"
          >
            <Play className={`h-3.5 w-3.5 ${isExecuting ? 'animate-pulse' : ''}`} />
            <span>{isExecuting ? 'Running...' : 'Run Query'}</span>
          </button>
        </div>
      </div>

      {/* Monaco Editor Container */}
      <div className="flex-1 min-h-[200px] bg-[#1e1e2e]">
        <Editor
          height="100%"
          language="sql"
          theme="vs-dark"
          value={value}
          onChange={(val) => onChange(val || '')}
          onMount={handleEditorDidMount}
          options={editorOptions}
          loading={
            <div className="flex items-center justify-center h-full bg-[#1e1e2e] text-slate-400 text-xs">
              Loading editor...
            </div>
          }
        />
      </div>
    </div>
  );
}
