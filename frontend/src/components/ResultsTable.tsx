import { useState } from 'react';
import { Download, Table, Inbox, AlertTriangle } from 'lucide-react';
import type { QueryResult, TimingInfo } from '../types';

interface ResultsTableProps {
  result: QueryResult | null;
  timings: TimingInfo | null;
  status: 'initial' | 'generating' | 'validating' | 'recovering' | 'success' | 'error';
  errorMessage: string | null;
}

export default function ResultsTable({ result, timings, status, errorMessage }: ResultsTableProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const rowsPerPage = 10;

  if (status === 'generating' || status === 'validating' || status === 'recovering') {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#1e1e2e]/20 border border-slate-800 rounded-xl h-64">
        <div className="flex gap-1.5 items-center mb-3">
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.3s]"></span>
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce [animation-delay:-0.15s]"></span>
          <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-bounce"></span>
        </div>
        <p className="text-sm font-medium text-indigo-300">
          {status === 'generating' && 'Generating SQL with SQLCoder-7B...'}
          {status === 'validating' && 'Validating execution in DuckDB...'}
          {status === 'recovering' && 'Self-correcting query error in model recovery loop...'}
        </p>
        <span className="text-xs text-slate-500 mt-1">This might take a few seconds</span>
      </div>
    );
  }

  if (status === 'error' && errorMessage) {
    return (
      <div className="p-6 bg-[#1a1012] border border-red-950/60 rounded-xl flex gap-3.5 items-start">
        <AlertTriangle className="h-5.5 w-5.5 text-red-500 shrink-0 mt-0.5" />
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-red-200">Execution Error</h4>
          <p className="text-xs text-red-400 mt-1 font-mono break-all whitespace-pre-wrap bg-red-950/20 p-3 rounded-lg border border-red-950/50">
            {errorMessage}
          </p>
        </div>
      </div>
    );
  }

  if (status === 'initial' || !result) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#1e1e2e]/20 border border-slate-800 rounded-xl h-64 text-slate-500">
        <Table className="h-10 w-10 text-slate-700 mb-3" />
        <p className="text-sm">No query results to display.</p>
        <span className="text-xs text-slate-600 mt-1">Submit a question or write custom SQL to run</span>
      </div>
    );
  }

  const { columns, rows, row_count, truncated } = result;

  if (row_count === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 bg-[#1e1e2e]/20 border border-slate-800 rounded-xl h-64 text-slate-500">
        <Inbox className="h-10 w-10 text-slate-700 mb-3" />
        <p className="text-sm">Query ran successfully but returned 0 rows.</p>
      </div>
    );
  }

  // Local Pagination Calculations
  const indexOfLastRow = currentPage * rowsPerPage;
  const indexOfFirstRow = indexOfLastRow - rowsPerPage;
  const currentRows = rows.slice(indexOfFirstRow, indexOfLastRow);
  const totalPages = Math.ceil(rows.length / rowsPerPage);

  const handleExportCSV = () => {
    // Generate CSV string
    const csvContent = [
      columns.map(c => `"${c.replace(/"/g, '""')}"`).join(','),
      ...rows.map(row => row.map(val => {
        const strVal = val === null ? '' : String(val);
        return `"${strVal.replace(/"/g, '""')}"`;
      }).join(','))
    ].join('\n');

    // Trigger browser download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `query_results_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="flex flex-col bg-[#1e1e2e]/30 border border-slate-800 rounded-xl overflow-hidden">
      {/* Header Panel */}
      <div className="flex items-center justify-between px-4 py-3 bg-[#1e1e2e]/80 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-slate-300">QUERY RESULTS</span>
          <span className="text-[11px] bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full font-mono">
            {row_count} {row_count === 1 ? 'row' : 'rows'} {truncated && '(truncated)'}
          </span>
          {timings && (
            <span className="text-[10px] text-slate-500">
              {timings.execution_ms !== null && timings.execution_ms !== undefined ? (
                `Executed in ${timings.execution_ms}ms`
              ) : timings.total_ms ? (
                `Processed in ${timings.total_ms}ms`
              ) : ''}
            </span>
          )}
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-slate-800/80 transition-colors cursor-pointer"
          title="Export CSV"
        >
          <Download className="h-3.5 w-3.5" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Table Container */}
      <div className="overflow-x-auto max-h-[400px]">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-slate-800 bg-[#11111b]/40">
              {columns.map((col) => (
                <th
                  key={col}
                  className="sticky top-0 px-4 py-3 text-xs font-semibold text-slate-400 bg-[#141423] font-mono border-b border-slate-800"
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {currentRows.map((row, idx) => (
              <tr
                key={idx}
                className="hover:bg-slate-800/20 text-xs transition-colors"
              >
                {row.map((cell, cellIdx) => (
                  <td key={cellIdx} className="px-4 py-2.5 font-mono text-slate-300">
                    {cell === null ? (
                      <span className="text-slate-600 italic">NULL</span>
                    ) : typeof cell === 'boolean' ? (
                      String(cell).toUpperCase()
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between px-4 py-3 bg-[#11111b]/20 border-t border-slate-800 text-xs">
          <span className="text-slate-500">
            Showing <span className="font-semibold text-slate-400">{indexOfFirstRow + 1}</span> to{' '}
            <span className="font-semibold text-slate-400">
              {Math.min(indexOfLastRow, rows.length)}
            </span>{' '}
            of <span className="font-semibold text-slate-400">{rows.length}</span> rows
          </span>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-2.5 py-1.5 rounded bg-slate-800/50 hover:bg-slate-800 disabled:opacity-40 text-slate-300 disabled:cursor-not-allowed font-medium"
            >
              Previous
            </button>
            <span className="text-slate-400 px-2">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-2.5 py-1.5 rounded bg-slate-800/50 hover:bg-slate-800 disabled:opacity-40 text-slate-300 disabled:cursor-not-allowed font-medium"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
