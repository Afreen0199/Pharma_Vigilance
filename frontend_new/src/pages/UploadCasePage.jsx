import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Upload, File, Image as ImageIcon, X, CheckCircle, Loader2,
  FileText, AlertCircle, Scan, Brain, Database, Shield, FlaskConical
} from 'lucide-react';
import { analysisApi } from '../api/analysisApi';

const PIPELINE_STAGES = [
  { id: 'upload', label: 'Upload Complete', icon: Upload },
  { id: 'ocr', label: 'OCR Extraction', icon: Scan },
  { id: 'entity', label: 'Entity Recognition', icon: Brain },
  { id: 'milvus', label: 'Milvus Hybrid Search', icon: Database },
  { id: 'fda', label: 'FDA Signal Retrieval', icon: FlaskConical },
  { id: 'ai', label: 'AI Safety Analysis', icon: Shield },
  { id: 'report', label: 'Report Generation', icon: FileText },
  { id: 'done', label: 'Analysis Complete', icon: CheckCircle },
];

const UploadCasePage = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [textInput, setTextInput] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(-1);
  const [error, setError] = useState(null);

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files?.[0]) handleValidFile(e.dataTransfer.files[0]);
  };

  const handleValidFile = (f) => {
    const valid = ['pdf', 'docx', 'txt', 'png', 'jpg', 'jpeg'];
    const ext = f.name.split('.').pop().toLowerCase();
    if (valid.includes(ext)) {
      setFile(f);
      setTextInput('');
      setError(null);
    } else {
      setError('Invalid file type. Supported: PDF, DOCX, TXT, PNG, JPG, JPEG.');
    }
  };

  const animateStages = (totalMs) => {
    const stageMs = totalMs / PIPELINE_STAGES.length;
    PIPELINE_STAGES.forEach((_, i) => {
      setTimeout(() => setCurrentStage(i), i * stageMs);
    });
  };

  const startAnalysis = async () => {
    if (!file && !textInput.trim()) {
      setError('Please provide a file or paste a case narrative.');
      return;
    }
    setIsProcessing(true);
    setCurrentStage(0);
    setError(null);

    // Animate stages while waiting for backend (estimated 45s max)
    animateStages(40000);

    try {
      let response;
      if (file) {
        const formData = new FormData();
        formData.append('file', file);
        response = await analysisApi.uploadCase(formData);
      } else {
        response = await analysisApi.analyzeText(textInput);
      }

      const analysisId = response.analysis_id || response.report?.analysis_id;
      if (!analysisId) throw new Error('No analysis_id returned from backend.');

      setCurrentStage(PIPELINE_STAGES.length - 1);
      setTimeout(() => navigate(`/analysis/${analysisId}`), 800);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || err.message || 'An error occurred during analysis.');
      setIsProcessing(false);
      setCurrentStage(-1);
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Upload Case for Analysis</h1>
        <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">
          Upload clinical narratives, scanned ADR forms, or handwritten prescriptions. Images are processed with AWS Textract OCR.
        </p>
      </div>

      {error && (
        <div className="flex items-start gap-2 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-700/50 rounded-xl text-sm font-semibold text-red-600 dark:text-red-400">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          {error}
        </div>
      )}

      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 space-y-6 shadow-sm dark:shadow-none">
        {/* Dropzone */}
        <div
          className={`border-2 border-dashed rounded-xl p-12 text-center transition-all cursor-pointer ${isDragging ? 'border-violet-500 bg-violet-50 dark:bg-violet-500/10' : 'border-slate-300 dark:border-slate-700 bg-slate-50 dark:bg-slate-950/50 hover:border-violet-400 dark:hover:border-violet-600/50 hover:bg-slate-100 dark:hover:bg-slate-800/30'} ${isProcessing ? 'pointer-events-none opacity-50' : ''}`}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => !file && fileInputRef.current?.click()}
        >
          <Upload className="mx-auto h-12 w-12 text-slate-400 dark:text-slate-600 mb-4" />
          <h3 className="text-lg font-semibold text-slate-700 dark:text-slate-300">Drag & drop a case file here</h3>
          <p className="text-xs text-slate-500 mt-2">PDF, DOCX, TXT, PNG, JPG, JPEG • Scanned images & handwritten forms supported</p>
          <button
            type="button"
            onClick={(e) => { e.stopPropagation(); fileInputRef.current?.click(); }}
            disabled={isProcessing}
            className="mt-5 px-5 py-2 bg-white dark:bg-slate-800 hover:bg-slate-50 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 text-sm font-semibold rounded-lg border border-slate-200 dark:border-slate-700 transition-all shadow-sm dark:shadow-none"
          >
            Browse Files
          </button>
          <input
            type="file"
            className="hidden"
            ref={fileInputRef}
            onChange={(e) => { if (e.target.files?.[0]) handleValidFile(e.target.files[0]); }}
            accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
          />
        </div>

        {/* Selected file */}
        {file && (
          <div className="flex items-center gap-3 p-4 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl">
            {file.type.startsWith('image/') ? <ImageIcon className="h-6 w-6 text-cyan-500 dark:text-cyan-400 shrink-0" /> : <File className="h-6 w-6 text-violet-600 dark:text-violet-400 shrink-0" />}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB • {file.type.startsWith('image/') ? 'OCR will be applied' : 'Direct text extraction'}</p>
            </div>
            {!isProcessing && (
              <button onClick={() => setFile(null)} className="text-slate-400 hover:text-red-500 dark:text-slate-500 dark:hover:text-red-400 transition-colors">
                <X className="h-5 w-5" />
              </button>
            )}
          </div>
        )}

        {/* Text narrative alternative */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <div className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
            <span className="text-xs text-slate-500 font-bold uppercase tracking-wider">or paste narrative text</span>
            <div className="h-px flex-1 bg-slate-200 dark:bg-slate-800" />
          </div>
          <textarea
            className="w-full h-28 p-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-700 rounded-xl text-sm text-slate-800 dark:text-slate-300 placeholder-slate-400 dark:placeholder-slate-600 focus:ring-2 focus:ring-violet-600/50 focus:outline-none focus:border-violet-600/50 resize-none transition-all"
            placeholder="Paste the case narrative, patient summary, or ADR description here..."
            value={textInput}
            onChange={(e) => { setTextInput(e.target.value); if (e.target.value) setFile(null); }}
            disabled={isProcessing || !!file}
          />
        </div>

        {/* Pipeline stages tracker */}
        {isProcessing && (
          <div className="bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-xl p-5">
            <h4 className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin text-violet-600 dark:text-violet-400" />
              AI Processing Pipeline — Please wait up to 60 seconds
            </h4>
            <div className="space-y-3">
              {PIPELINE_STAGES.map((stage, idx) => {
                const done = idx < currentStage;
                const active = idx === currentStage;
                const pending = idx > currentStage;
                return (
                  <div key={stage.id} className={`flex items-center gap-3 transition-all duration-500 ${pending ? 'opacity-30' : 'opacity-100'}`}>
                    <div className={`h-8 w-8 rounded-full flex items-center justify-center shrink-0 transition-all ${done ? 'bg-emerald-100 dark:bg-emerald-600/20 text-emerald-600 dark:text-emerald-400' : active ? 'bg-violet-100 dark:bg-violet-600/30 text-violet-600 dark:text-violet-400' : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600'}`}>
                      {done ? (
                        <CheckCircle className="h-4 w-4" />
                      ) : active ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <stage.icon className="h-4 w-4" />
                      )}
                    </div>
                    <span className={`text-sm font-semibold ${done ? 'text-emerald-400' : active ? 'text-violet-300' : 'text-slate-500'}`}>
                      {stage.label}
                    </span>
                    {done && <span className="ml-auto text-[10px] text-emerald-500 font-bold">✓ DONE</span>}
                    {active && <span className="ml-auto text-[10px] text-violet-400 font-bold animate-pulse">● RUNNING</span>}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Submit button */}
        {!isProcessing && (
          <button
            onClick={startAnalysis}
            disabled={!file && !textInput.trim()}
            className="w-full py-3.5 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-100 dark:disabled:bg-slate-800 disabled:text-slate-400 dark:disabled:text-slate-600 text-white text-sm font-bold rounded-xl transition-all shadow-lg shadow-violet-600/20 flex items-center justify-center gap-2"
          >
            <Brain className="h-5 w-5" />
            Begin AI Analysis Pipeline
          </button>
        )}
      </div>
    </div>
  );
};

export default UploadCasePage;
