import React, { useState, useEffect } from 'react';
import { kbApi } from '../api/kbApi';
import { 
  Database, 
  Upload, 
  Trash2, 
  FileText, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  RefreshCw,
  HardDrive
} from 'lucide-react';

const KnowledgeBasePage = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const fetchDocuments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await kbApi.listDocuments();
      setDocuments(data || []);
    } catch (err) {
      console.error('List documents error:', err);
      setError('Failed to fetch guidelines collection from Milvus database. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const res = await kbApi.uploadDocument(file);
      setSuccessMsg(`Document '${file.name}' ingested and chunked successfully!`);
      // Refresh list
      await fetchDocuments();
    } catch (err) {
      console.error('Upload document error:', err);
      setError(err.response?.data?.detail || 'Failed to ingest document to Milvus collection.');
    } finally {
      setUploading(false);
      // Clear file input
      e.target.value = '';
    }
  };

  const handleDelete = async (docName) => {
    if (!window.confirm(`Are you sure you want to delete guidelines document '${docName}' from the safety knowledge base?`)) return;

    setError(null);
    setSuccessMsg(null);

    try {
      await kbApi.deleteDocument(docName);
      setSuccessMsg(`Successfully removed safety reference document '${docName}'.`);
      await fetchDocuments();
    } catch (err) {
      console.error('Delete document error:', err);
      setError('Failed to delete safety reference document.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
            Safety Knowledge Base
          </h1>
          <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase mt-0.5 tracking-wider">
            Manage CDSCO Warnings, FDA Guidances & FAERS reference sheets in Milvus DB
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchDocuments}
            disabled={loading}
            className="p-2 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400 rounded-lg transition-colors flex items-center justify-center"
            title="Refresh Guidelines List"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          
          <label className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-bold shadow-md shadow-brand-600/20 cursor-pointer transition-all">
            <Upload className="h-4 w-4" />
            <span>Ingest Document</span>
            <input
              type="file"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
              accept=".pdf,.docx,.txt"
            />
          </label>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900/50 rounded-xl text-xs font-bold text-red-600 dark:text-red-400 flex items-start gap-2">
          <AlertCircle className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 rounded-xl text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-start gap-2">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Main Grid: Upload Loader & Documents List */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-sm p-6 space-y-4">
        
        {/* Upload Status Card */}
        {uploading && (
          <div className="p-5 bg-brand-50/50 dark:bg-brand-950/20 border border-brand-200/50 dark:border-brand-900/30 rounded-xl flex items-center gap-4">
            <Loader2 className="h-6 w-6 animate-spin text-brand-500 shrink-0" />
            <div>
              <h4 className="text-xs font-bold text-brand-700 dark:text-brand-400 uppercase tracking-wide">
                Ingesting safety document
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 leading-normal mt-0.5">
                Parsing references, executing semantic token chunking, generating embeddings, and building indexes in Milvus vector store.
              </p>
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">
            Ingested Guidelines & Warning References
          </h3>
          <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider">
            Milvus Collections Database
          </span>
        </div>

        {loading ? (
          <div className="h-60 flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="h-8 w-8 animate-spin text-brand-500 mb-2" />
            <span className="text-xs font-semibold">Reading guidelines directory...</span>
          </div>
        ) : documents.length === 0 ? (
          <div className="h-60 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl flex flex-col items-center justify-center p-6 text-center">
            <HardDrive className="h-10 w-10 text-slate-300 dark:text-slate-700 mb-2.5" />
            <p className="text-xs font-bold text-slate-600 dark:text-slate-400">No reference documents ingested</p>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-1 max-w-xs">
              Upload FDA warning documents or CDSCO banned substances sheets to enable semantic retrieval and chatbot grounding.
            </p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-100 dark:border-slate-800 text-[10px] text-slate-400 dark:text-slate-500 font-extrabold uppercase">
                  <th className="pb-3">Document Source</th>
                  <th className="pb-3">Type</th>
                  <th className="pb-3 text-center">Segments / Chunks</th>
                  <th className="pb-3 text-right">Delete</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/50 text-xs">
                {documents.map((doc, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/20 transition-all">
                    <td className="py-3.5 font-semibold text-slate-700 dark:text-slate-300 flex items-center gap-2">
                      <FileText className="h-4.5 w-4.5 text-brand-600 dark:text-brand-400 shrink-0" />
                      <span className="truncate max-w-sm" title={doc.document_name}>
                        {doc.document_name}
                      </span>
                    </td>
                    <td className="py-3.5 font-semibold text-slate-400">
                      <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 rounded-md font-bold text-[9px] uppercase">
                        {doc.document_name?.toLowerCase().endsWith('.pdf') ? 'PDF Guide' : 'Document'}
                      </span>
                    </td>
                    <td className="py-3.5 text-center font-bold text-slate-800 dark:text-slate-300">
                      {doc.chunks_count || 'Pending'}
                    </td>
                    <td className="py-3.5 text-right">
                      <button
                        onClick={() => handleDelete(doc.document_name)}
                        className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-slate-50 dark:hover:bg-slate-800 rounded transition-all inline-flex items-center justify-center"
                        title="Remove Document from Milvus Store"
                      >
                        <Trash2 className="h-4.5 w-4.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgeBasePage;
