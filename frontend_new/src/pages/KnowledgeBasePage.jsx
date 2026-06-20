import React, { useState, useRef, useEffect } from 'react';
import { Upload, File, FileText, Database, Trash2, Loader2, CheckCircle, AlertCircle, X, RefreshCw } from 'lucide-react';
import { knowledgeApi } from '../api/knowledgeApi';

const KnowledgeBasePage = () => {
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [deletingDoc, setDeletingDoc] = useState(null);

  const fetchDocuments = async () => {
    setLoadingDocs(true);
    try {
      const res = await knowledgeApi.list();
      setDocuments(res.documents || []);
    } catch (e) {
      console.error('Failed to load KB documents:', e);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => { fetchDocuments(); }, []);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) handleValidFile(f);
  };

  const handleValidFile = (f) => {
    const valid = ['pdf', 'csv', 'docx', 'txt'];
    const ext = f.name.split('.').pop().toLowerCase();
    if (valid.includes(ext)) {
      setFile(f);
      setUploadResult(null);
      setUploadError(null);
    } else {
      setUploadError('Unsupported file type. Please use PDF, CSV, DOCX, or TXT.');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setUploadResult(null);
    setUploadError(null);
    const fd = new FormData();
    fd.append('file', file);
    try {
      const result = await knowledgeApi.upload(fd);
      setUploadResult(result);
      setFile(null);
      fetchDocuments();
    } catch (e) {
      setUploadError(e.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docName) => {
    if (!window.confirm(`Delete "${docName}" from the knowledge base?`)) return;
    setDeletingDoc(docName);
    try {
      await knowledgeApi.deleteDocument(docName);
      fetchDocuments();
    } catch (e) {
      alert(e.response?.data?.detail || 'Delete failed.');
    } finally {
      setDeletingDoc(null);
    }
  };

  const extIcon = (name) => {
    const ext = name?.split('.').pop().toLowerCase();
    const colors = { pdf: 'text-red-400', csv: 'text-green-400', docx: 'text-blue-400', txt: 'text-slate-400' };
    return <FileText className={`h-5 w-5 ${colors[ext] || 'text-slate-400'}`} />;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Knowledge Base Management</h1>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">Upload regulatory guidelines and drug safety reference documents to power the AI copilot.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-start">
        {/* Upload panel */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-4 shadow-sm dark:shadow-none">
          <div className="flex items-center gap-2 mb-2">
            <Upload className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            <h2 className="text-sm font-bold text-slate-800 dark:text-slate-300 uppercase tracking-wider">Upload Document</h2>
          </div>

          <div
            className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer ${isDragging ? 'border-violet-500 bg-violet-50 dark:bg-violet-500/10' : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/50 hover:border-violet-400 dark:hover:border-violet-600/50 hover:bg-slate-100 dark:hover:bg-slate-800/30'}`}
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => !file && fileInputRef.current?.click()}
          >
            <Database className="mx-auto h-10 w-10 text-slate-400 dark:text-slate-600 mb-3" />
            <p className="text-sm font-semibold text-slate-700 dark:text-slate-300">Drag & drop file here</p>
            <p className="text-xs text-slate-500 mt-1">PDF, CSV, DOCX, TXT supported</p>
            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              accept=".pdf,.csv,.docx,.txt"
              onChange={(e) => { if (e.target.files[0]) handleValidFile(e.target.files[0]); }}
            />
          </div>

          {file && (
            <div className="flex items-center gap-3 p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl">
              {extIcon(file.name)}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">{file.name}</p>
                <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button onClick={() => setFile(null)} className="text-slate-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {uploadError && (
            <div className="flex items-start gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/50 rounded-xl text-xs font-semibold text-red-600 dark:text-red-400">
              <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
              {uploadError}
            </div>
          )}

          {uploadResult && (
            <div className="p-3 bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-700/50 rounded-xl space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-emerald-600 dark:text-emerald-400">
                <CheckCircle className="h-4 w-4" />
                Ingestion Successful
              </div>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {[
                  ['Chunks Indexed', uploadResult.chunks_indexed],
                  ['Text Length', `${uploadResult.extracted_text_length?.toLocaleString()} chars`],
                  ['Collection', uploadResult.destination_collection],
                  ['Status', uploadResult.status],
                ].map(([k, v]) => (
                  <div key={k} className="bg-white dark:bg-slate-900 rounded-lg p-2 border border-slate-100 dark:border-slate-800 shadow-sm dark:shadow-none">
                    <p className="text-[10px] text-slate-500 uppercase font-bold">{k}</p>
                    <p className="text-xs text-slate-800 dark:text-slate-200 font-semibold">{v}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || uploading}
            className="w-full py-3 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-200 dark:disabled:bg-slate-700 disabled:text-slate-400 dark:disabled:text-slate-500 text-white text-sm font-bold rounded-xl transition-all flex items-center justify-center gap-2"
          >
            {uploading ? (
              <><Loader2 className="h-4 w-4 animate-spin" /> Indexing into Milvus...</>
            ) : (
              <><Upload className="h-4 w-4" /> Upload to Knowledge Base</>
            )}
          </button>
        </div>

        {/* Indexed Documents */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm dark:shadow-none">
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="h-4 w-4 text-violet-600 dark:text-violet-400" />
              <h2 className="text-sm font-bold text-slate-800 dark:text-slate-300 uppercase tracking-wider">Indexed Documents</h2>
            </div>
            <button onClick={fetchDocuments} className="text-slate-500 hover:text-slate-800 dark:hover:text-slate-300 transition-colors" title="Refresh">
              <RefreshCw className={`h-4 w-4 ${loadingDocs ? 'animate-spin' : ''}`} />
            </button>
          </div>

          <div className="divide-y divide-slate-200 dark:divide-slate-800 max-h-[400px] overflow-y-auto">
            {loadingDocs ? (
              Array(4).fill(0).map((_, i) => (
                <div key={i} className="flex items-center gap-3 px-6 py-4">
                  <div className="h-5 w-5 bg-slate-200 dark:bg-slate-800 animate-pulse rounded" />
                  <div className="flex-1 h-4 bg-slate-200 dark:bg-slate-800 animate-pulse rounded" />
                </div>
              ))
            ) : documents.length === 0 ? (
              <div className="px-6 py-12 text-center text-slate-500 dark:text-slate-600 text-sm">
                No documents indexed yet. Upload a file to get started.
              </div>
            ) : documents.map((doc, i) => (
              <div key={i} className="flex items-center gap-3 px-6 py-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                {extIcon(doc.document_name)}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">{doc.document_name}</p>
                  <p className="text-xs text-slate-500 capitalize">{doc.document_type?.replace(/_/g, ' ')}</p>
                </div>
                <button
                  onClick={() => handleDelete(doc.document_name)}
                  disabled={deletingDoc === doc.document_name}
                  className="text-slate-400 dark:text-slate-600 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                >
                  {deletingDoc === doc.document_name
                    ? <Loader2 className="h-4 w-4 animate-spin" />
                    : <Trash2 className="h-4 w-4" />
                  }
                </button>
              </div>
            ))}
          </div>

          {documents.length > 0 && (
            <div className="px-6 py-3 bg-slate-50/50 dark:bg-slate-950/50 border-t border-slate-200 dark:border-slate-800">
              <p className="text-xs text-slate-500">{documents.length} document{documents.length !== 1 ? 's' : ''} indexed in Milvus knowledge_base collection</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default KnowledgeBasePage;
