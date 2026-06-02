import { useState, useEffect } from 'react';
import { Terminal, Database, RefreshCw, Send, Code2, AlertCircle } from 'lucide-react';
import SchemaBrowser from './components/SchemaBrowser';
import MonacoSqlEditor from './components/MonacoSqlEditor';
import ResultsTable from './components/ResultsTable';
import RecoveryTimeline from './components/RecoveryTimeline';
import HistoryPanel from './components/HistoryPanel';
import type { SchemaInfo, GenerateResponse, QueryResult, ValidationResult, TimingInfo } from './types';

const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [schemas, setSchemas] = useState<SchemaInfo[]>([]);
  const [activeSchema, setActiveSchema] = useState<SchemaInfo | null>(null);
  
  // Input and generation state
  const [question, setQuestion] = useState('');
  const [sql, setSql] = useState('SELECT * FROM customers LIMIT 5;');
  const [generatedSql, setGeneratedSql] = useState('SELECT * FROM customers LIMIT 5;');
  
  // Execution outcome state
  const [status, setStatus] = useState<'initial' | 'generating' | 'validating' | 'recovering' | 'success' | 'error'>('initial');
  const [validation, setValidation] = useState<ValidationResult | null>(null);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [timings, setTimings] = useState<TimingInfo | null>(null);
  const [recovery, setRecovery] = useState<any[]>([]);
  
  // History state (saved in localstorage)
  const [history, setHistory] = useState<GenerateResponse[]>([]);
  const [activeHistoryId, setActiveHistoryId] = useState<string | null>(null);
  
  // Connection and system states
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [isLoadingSchema, setIsLoadingSchema] = useState(true);
  const [isExecuting, setIsExecuting] = useState(false);

  // Load history on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('text_to_sql_history');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to parse history', e);
      }
    }
    checkBackendHealth();
  }, []);

  // Check health and load schemas
  const checkBackendHealth = async () => {
    setBackendStatus('checking');
    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) {
        setBackendStatus('online');
        loadSchemas();
      } else {
        setBackendStatus('offline');
        setIsLoadingSchema(false);
      }
    } catch (e) {
      setBackendStatus('offline');
      setIsLoadingSchema(false);
    }
  };

  const loadSchemas = async () => {
    setIsLoadingSchema(true);
    try {
      const res = await fetch(`${API_BASE_URL}/schemas`);
      if (res.ok) {
        const data = await res.json();
        setSchemas(data.schemas);
        if (data.schemas.length > 0) {
          setActiveSchema(data.schemas[0]);
        }
      }
    } catch (e) {
      console.error('Failed to load schemas', e);
    } finally {
      setIsLoadingSchema(false);
    }
  };

  const handleGenerate = async () => {
    if (!question.trim() || !activeSchema) return;
    
    setStatus('generating');
    setResult(null);
    setValidation(null);
    setTimings(null);
    setRecovery([]);
    setIsExecuting(true);

    try {
      const res = await fetch(`${API_BASE_URL}/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: question,
          schema_id: activeSchema.schema_id,
          max_retries: 2,
          execute: true,
          row_limit: 100
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to generate SQL');
      }

      const data: GenerateResponse = await res.json();
      
      setSql(data.final_sql);
      setGeneratedSql(data.generated_sql);
      setValidation(data.validation);
      setResult(data.result);
      setTimings(data.timings);
      setRecovery(data.recovery || []);
      
      // Determine final status
      if (data.status === 'success') {
        setStatus('success');
      } else {
        setStatus('error');
      }

      // If recovery was running, update state
      if (data.recovery && data.recovery.length > 0) {
        const hasSuccessAttempt = data.recovery.some(a => a.status === 'success');
        if (hasSuccessAttempt) {
          setStatus('success');
        }
      }

      // Save to history
      const updatedHistory = [data, ...history].slice(0, 50); // limit to 50 items
      setHistory(updatedHistory);
      localStorage.setItem('text_to_sql_history', JSON.stringify(updatedHistory));
      setActiveHistoryId(data.request_id);

    } catch (e: any) {
      setStatus('error');
      setValidation({
        is_valid: false,
        is_safe: true,
        error_type: 'API_ERROR',
        error_message: e.message || 'API request failed'
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleExecute = async () => {
    if (!sql.trim() || !activeSchema) return;

    setStatus('validating');
    setIsExecuting(true);

    try {
      const res = await fetch(`${API_BASE_URL}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          sql: sql,
          schema_id: activeSchema.schema_id,
          row_limit: 100
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to execute SQL');
      }

      const data = await res.json();
      
      setValidation(data.validation);
      setResult(data.result);
      setTimings(data.timings);
      
      if (data.status === 'success') {
        setStatus('success');
      } else {
        setStatus('error');
      }
    } catch (e: any) {
      setStatus('error');
      setValidation({
        is_valid: false,
        is_safe: true,
        error_type: 'API_ERROR',
        error_message: e.message || 'Execution request failed'
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const handleSelectHistory = (item: GenerateResponse) => {
    setQuestion(item.question);
    setSql(item.final_sql);
    setGeneratedSql(item.generated_sql);
    setValidation(item.validation);
    setResult(item.result);
    setTimings(item.timings);
    setRecovery(item.recovery || []);
    
    // Determine status
    if (item.status === 'success') {
      setStatus('success');
    } else {
      setStatus('error');
    }
    setActiveHistoryId(item.request_id);
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem('text_to_sql_history');
    setActiveHistoryId(null);
  };

  const handleReset = () => {
    setSql(generatedSql);
  };

  const handleInsertText = (text: string) => {
    // Append table/column name to question or editor
    setQuestion(prev => prev + (prev.endsWith(' ') || prev === '' ? '' : ' ') + text);
  };

  const hasChanges = sql.trim() !== generatedSql.trim();

  return (
    <div className="flex flex-col h-screen bg-[#0c0c14] text-slate-100 font-sans">
      {/* Top Bar Glass Panel */}
      <header className="flex items-center justify-between px-6 py-4 bg-[#11111b]/80 border-b border-slate-900 backdrop-blur-md z-30 shrink-0">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-600/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <Terminal className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-md font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              text-to-sql-ai
            </h1>
            <p className="text-[10px] text-slate-500 font-medium">QLoRA Adapter Fine-Tuned Query Workbench</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Active Schema Selector */}
          {activeSchema && (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-[#1e1e2e]/80 border border-slate-800 rounded-lg text-xs">
              <Database className="h-3.5 w-3.5 text-indigo-400" />
              <select
                value={activeSchema.schema_id}
                onChange={(e) => {
                  const selected = schemas.find(s => s.schema_id === e.target.value);
                  if (selected) setActiveSchema(selected);
                }}
                className="bg-transparent text-slate-300 font-medium font-mono focus:outline-none cursor-pointer"
              >
                {schemas.map(s => (
                  <option key={s.schema_id} value={s.schema_id} className="bg-[#1e1e2e] text-slate-300">
                    {s.schema_id}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Backend Connection Indicator */}
          <div className="flex items-center gap-2">
            <button 
              onClick={checkBackendHealth}
              className="p-1 hover:bg-slate-800/80 rounded transition-colors text-slate-400"
              title="Refresh connection status"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${backendStatus === 'checking' ? 'animate-spin' : ''}`} />
            </button>
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold ${
              backendStatus === 'online' 
                ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' 
                : backendStatus === 'offline'
                ? 'bg-red-500/10 border-red-500/20 text-red-400 animate-pulse'
                : 'bg-slate-800/50 border-slate-700/50 text-slate-400'
            }`}>
              <span className={`h-2 w-2 rounded-full ${
                backendStatus === 'online' ? 'bg-emerald-500 animate-pulse' : backendStatus === 'offline' ? 'bg-red-500' : 'bg-slate-500'
              }`} />
              <span>{backendStatus.toUpperCase()}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden p-4 gap-4">
        {/* Left Side: Schema Browser */}
        <aside className="w-80 shrink-0 h-full overflow-hidden">
          <SchemaBrowser
            schema={activeSchema}
            isLoading={isLoadingSchema}
            onInsertText={handleInsertText}
          />
        </aside>

        {/* Center: Question Input, Editor, Results */}
        <main className="flex-1 flex flex-col h-full overflow-y-auto pr-1 space-y-4">
          
          {/* Question Input Card */}
          <section className="bg-[#1e1e2e]/50 border border-slate-800/80 rounded-xl p-5 shadow-lg relative overflow-hidden group shrink-0">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <Code2 className="h-24 w-24 text-slate-400" />
            </div>
            
            <h2 className="text-xs font-semibold text-slate-400 mb-3.5 uppercase tracking-wider">
              Ask a Relational Question
            </h2>
            
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <textarea
                  rows={2}
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="Ask a question about the database (e.g. 'What were the top 5 products by revenue?')"
                  className="w-full bg-[#11111b]/80 border border-slate-800 hover:border-slate-700 focus:border-indigo-500 focus:outline-none rounded-xl p-4 text-sm text-slate-100 placeholder-slate-500 resize-none transition-colors"
                />
                
                {/* Suggestions Helper */}
                <div className="flex gap-2 mt-2">
                  <button 
                    onClick={() => setQuestion("Which customers placed the most orders? (fail)")}
                    className="text-[10px] text-slate-500 hover:text-indigo-400 bg-[#11111b]/40 hover:bg-[#11111b]/80 border border-slate-800/80 px-2 py-0.5 rounded transition-all"
                  >
                    Demo Error Recovery (uses fail)
                  </button>
                  <button 
                    onClick={() => setQuestion("What were the top 5 products by revenue?")}
                    className="text-[10px] text-slate-500 hover:text-indigo-400 bg-[#11111b]/40 hover:bg-[#11111b]/80 border border-slate-800/80 px-2 py-0.5 rounded transition-all"
                  >
                    Top Products by Revenue
                  </button>
                </div>
              </div>

              <div className="shrink-0 flex flex-col">
                <button
                  onClick={handleGenerate}
                  disabled={isExecuting || !question.trim() || backendStatus !== 'online'}
                  className="flex-1 px-5 py-3 rounded-xl font-semibold text-sm bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-800 disabled:to-slate-800 text-white shadow-lg shadow-indigo-950/20 hover:shadow-indigo-500/10 disabled:shadow-none flex flex-col items-center justify-center gap-1.5 transition-all cursor-pointer disabled:cursor-not-allowed min-w-[120px]"
                >
                  <Send className="h-4 w-4" />
                  <span>Generate SQL</span>
                </button>
              </div>
            </div>
          </section>

          {/* SQL Editor Container */}
          <section className="h-[340px] shrink-0">
            <MonacoSqlEditor
              value={sql}
              onChange={setSql}
              onExecute={handleExecute}
              onReset={handleReset}
              isExecuting={isExecuting}
              hasChanges={hasChanges}
            />
          </section>

          {/* Query Execution Status Panel */}
          {validation && !validation.is_valid && validation.error_message && (
            <section className="bg-red-950/15 border border-red-900/40 rounded-xl p-4 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
              <div>
                <h4 className="text-xs font-bold text-red-300">VALIDATION WARNING</h4>
                <p className="text-xs text-red-400/90 mt-1 font-mono">{validation.error_message}</p>
              </div>
            </section>
          )}

          {/* Results Table Panel */}
          <section className="flex-1">
            <ResultsTable
              result={result}
              timings={timings}
              status={status}
              errorMessage={validation && !validation.is_valid ? validation.error_message : null}
            />
          </section>

          {/* Recovery timeline */}
          {recovery.length > 0 && (
            <section className="shrink-0">
              <RecoveryTimeline attempts={recovery} />
            </section>
          )}
        </main>

        {/* Right Side: Query History Panel */}
        <aside className="w-80 shrink-0 h-full overflow-hidden">
          <HistoryPanel
            history={history}
            onSelectHistory={handleSelectHistory}
            onClearHistory={handleClearHistory}
            activeId={activeHistoryId}
          />
        </aside>
      </div>
    </div>
  );
}

// End of App Component
