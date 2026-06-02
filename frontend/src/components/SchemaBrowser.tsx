import { useState } from 'react';
import { Database, Table2, Key, ArrowRight, Search, ChevronDown, ChevronRight, Copy, Check } from 'lucide-react';
import type { SchemaInfo } from '../types';

interface SchemaBrowserProps {
  schema: SchemaInfo | null;
  isLoading: boolean;
  onInsertText: (text: string) => void;
}

export default function SchemaBrowser({ schema, isLoading, onInsertText }: SchemaBrowserProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedTables, setExpandedTables] = useState<Record<string, boolean>>({
    customers: true, // expand customers by default
    orders: true,
  });
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const toggleTable = (tableName: string) => {
    setExpandedTables(prev => ({
      ...prev,
      [tableName]: !prev[tableName]
    }));
  };

  const handleCopy = (text: string, e: React.MouseEvent) => {
    e.stopPropagation();
    navigator.clipboard.writeText(text);
    setCopiedText(text);
    setTimeout(() => setCopiedText(null), 1500);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-slate-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500 mb-4"></div>
        <p className="text-sm">Loading schema metadata...</p>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="p-4 text-center text-slate-400 text-sm">
        No schema selected.
      </div>
    );
  }

  const filteredTables = schema.tables.filter(table => {
    const tableMatch = table.name.toLowerCase().includes(searchQuery.toLowerCase());
    const columnMatch = table.columns.some(col => col.name.toLowerCase().includes(searchQuery.toLowerCase()));
    return tableMatch || columnMatch;
  });

  return (
    <div className="flex flex-col h-full bg-[#1e1e2e]/50 border border-slate-800 rounded-xl overflow-hidden">
      {/* Schema Title & Selector */}
      <div className="p-4 border-b border-slate-800 bg-[#1e1e2e]/80 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-indigo-400" />
          <div>
            <h3 className="font-semibold text-slate-200 text-sm">Schema Browser</h3>
            <p className="text-xs text-slate-400">{schema.dialect.toUpperCase()} • {schema.name}</p>
          </div>
        </div>
      </div>

      {/* Search Input */}
      <div className="p-3 border-b border-slate-800 bg-[#11111b]/30">
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Filter tables/columns..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-[#11111b]/80 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
          />
        </div>
      </div>

      {/* Tables List */}
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        {filteredTables.length === 0 ? (
          <div className="text-center text-slate-500 py-8 text-xs">
            No matching tables or columns found.
          </div>
        ) : (
          filteredTables.map((table) => {
            const isExpanded = !!expandedTables[table.name];
            return (
              <div key={table.name} className="rounded-lg overflow-hidden transition-colors">
                {/* Table Header */}
                <div
                  onClick={() => toggleTable(table.name)}
                  className="flex items-center justify-between px-3 py-2 text-xs font-medium text-slate-300 hover:text-slate-100 hover:bg-slate-800/40 cursor-pointer rounded-lg"
                >
                  <div className="flex items-center gap-2">
                    {isExpanded ? (
                      <ChevronDown className="h-3.5 w-3.5 text-slate-400" />
                    ) : (
                      <ChevronRight className="h-3.5 w-3.5 text-slate-400" />
                    )}
                    <Table2 className="h-4 w-4 text-indigo-400" />
                    <span className="font-mono">{table.name}</span>
                    {table.row_count !== null && (
                      <span className="text-[10px] bg-slate-800/80 px-1.5 py-0.5 rounded-full text-slate-400">
                        {table.row_count} rows
                      </span>
                    )}
                  </div>
                  <button
                    onClick={(e) => handleCopy(table.name, e)}
                    className="opacity-0 group-hover:opacity-100 hover:text-indigo-400 p-0.5"
                    title="Copy table name"
                  >
                    {copiedText === table.name ? (
                      <Check className="h-3 w-3 text-emerald-400" />
                    ) : (
                      <Copy className="h-3 w-3" />
                    )}
                  </button>
                </div>

                {/* Columns (Expanded) */}
                {isExpanded && (
                  <div className="pl-7 pr-2 pb-2 pt-0.5 space-y-1 bg-[#11111b]/10 rounded-b-lg border-l border-indigo-950/30 ml-5 my-0.5">
                    {table.columns.map((col) => {
                      const isMatchedSearch = searchQuery && col.name.toLowerCase().includes(searchQuery.toLowerCase());
                      
                      return (
                        <div
                          key={col.name}
                          onClick={() => onInsertText(col.name)}
                          className={`group flex items-center justify-between px-2 py-1.5 text-[11px] rounded hover:bg-slate-800/50 cursor-pointer ${
                            isMatchedSearch ? 'bg-indigo-950/20 text-indigo-200' : 'text-slate-400 hover:text-slate-300'
                          }`}
                        >
                          <div className="flex items-center gap-2 overflow-hidden">
                            {col.is_primary_key ? (
                              <span title="Primary Key"><Key className="h-3 w-3 text-amber-500 shrink-0" /></span>
                            ) : col.references ? (
                              <span title="Foreign Key Reference"><ArrowRight className="h-3 w-3 text-emerald-500 shrink-0" /></span>
                            ) : (
                              <div className="w-3 h-3 shrink-0" />
                            )}
                            <span className="font-mono truncate">{col.name}</span>
                            <span className="text-[10px] text-slate-500 font-mono italic">
                              {col.type.toLowerCase()}
                            </span>
                          </div>
                          
                          <div className="flex items-center gap-1.5 shrink-0 pl-2">
                            {col.references && (
                              <span className="text-[9px] text-emerald-400 font-mono max-w-[80px] truncate" title={`References ${col.references}`}>
                                → {col.references.split('(')[0]}
                              </span>
                            )}
                            <button
                              onClick={(e) => handleCopy(col.name, e)}
                              className="opacity-0 group-hover:opacity-100 hover:text-indigo-400 p-0.5"
                              title="Copy column name"
                            >
                              {copiedText === col.name ? (
                                <Check className="h-2.5 w-2.5 text-emerald-400" />
                              ) : (
                                <Copy className="h-2.5 w-2.5" />
                              )}
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
