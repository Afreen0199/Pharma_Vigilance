import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';

const DragDropUploader = ({ onUploadSuccess, isProcessing, ocrSteps }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return;
    onUploadSuccess(file);
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 rounded-xl shadow-lg">
      <form onSubmit={handleSubmit} onDragEnter={handleDrag} className="space-y-6">
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx,.txt,.png,.jpg,.jpeg"
        />

        <div
          onClick={triggerFileInput}
          onDragOver={handleDrag}
          onDragLeave={handleDrag}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all duration-200 ${
            dragActive 
              ? 'border-brand-500 bg-brand-50/50 dark:bg-brand-950/20' 
              : 'border-slate-300 dark:border-slate-700 hover:border-brand-400 dark:hover:border-brand-500 bg-slate-50/50 dark:bg-slate-900/50'
          }`}
        >
          <div className="p-4 bg-brand-50 dark:bg-brand-950/50 text-brand-600 dark:text-brand-400 rounded-full">
            <Upload className="h-8 w-8" />
          </div>
          
          <div className="text-center">
            <p className="font-semibold text-slate-700 dark:text-slate-300">
              Drag and drop your medical report
            </p>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Supports PDF, DOCX, TXT, scanned PNG/JPG prescriptions
            </p>
          </div>
        </div>

        {file && (
          <div className="flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-800 rounded-lg">
            <div className="flex items-center gap-3">
              <FileText className="h-6 w-6 text-brand-500" />
              <div>
                <p className="text-sm font-semibold text-slate-800 dark:text-slate-200 truncate max-w-sm">
                  {file.name}
                </p>
                <p className="text-xs text-slate-400 font-medium">
                  {(file.size / 1024).toFixed(1)} KB
                </p>
              </div>
            </div>
            
            <button
              type="submit"
              disabled={isProcessing}
              className="px-5 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-sm font-semibold shadow-md shadow-brand-600/25 transition-all disabled:opacity-50"
            >
              Analyze Case
            </button>
          </div>
        )}
      </form>

      {/* OCR & Processing Pipeline Steps */}
      {isProcessing && (
        <div className="mt-8 border-t border-slate-200 dark:border-slate-800 pt-6 space-y-4">
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-2">
            <RefreshCw className="h-4 w-4 animate-spin text-brand-500" />
            <span>Case Processing Pipeline Status</span>
          </h4>
          
          <div className="space-y-3">
            {ocrSteps ? (
              ocrSteps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-3 text-sm">
                  {step.status === 'completed' && <CheckCircle className="h-5 w-5 text-emerald-500 flex-shrink-0" />}
                  {step.status === 'active' && <RefreshCw className="h-5 w-5 text-brand-500 animate-spin flex-shrink-0" />}
                  {step.status === 'pending' && <div className="h-5 w-5 rounded-full border border-slate-300 dark:border-slate-700 flex-shrink-0" />}
                  
                  <span className={`font-medium ${
                    step.status === 'completed' 
                      ? 'text-slate-800 dark:text-slate-300' 
                      : step.status === 'active' 
                      ? 'text-brand-600 dark:text-brand-400 font-semibold animate-pulse' 
                      : 'text-slate-400'
                  }`}>
                    {step.label}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-slate-400 text-sm italic">
                Extracting clinical findings, RAG warnings, and FDA evidence...
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DragDropUploader;
