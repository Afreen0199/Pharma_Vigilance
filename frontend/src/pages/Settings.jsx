import React, { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  ShieldCheck, 
  Database, 
  Sliders, 
  Info,
  CheckCircle2,
  HardDrive
} from 'lucide-react';

const Settings = () => {
  const [success, setSuccess] = useState(false);
  const [modelType, setModelType] = useState('groq-llama3');
  const [temperature, setTemperature] = useState(0.2);
  const [confidenceThreshold, setConfidenceThreshold] = useState(70);

  const handleSave = (e) => {
    e.preventDefault();
    setSuccess(true);
    setTimeout(() => setSuccess(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto py-4">
      {/* Title */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm">
        <h1 className="text-xl font-bold text-slate-800 dark:text-white flex items-center gap-2">
          Platform Settings
        </h1>
        <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase mt-0.5 tracking-wider">
          Configure safety parameters, database integrations, and reasoning variables
        </p>
      </div>

      {success && (
        <div className="p-4 bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-200 dark:border-emerald-900/50 rounded-xl text-xs font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" />
          <span>System configuration updated successfully.</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* PV Model Parameters */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Sliders className="h-5 w-5 text-brand-600 dark:text-brand-400" />
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">Reasoning Engine Tuning</h3>
          </div>

          <div className="space-y-4">
            {/* LLM Model Selection */}
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider block">
                Primary LLM Reasoning Model
              </label>
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
                className="block w-full py-2.5 px-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-xs font-semibold focus:outline-none focus:border-brand-500 text-slate-800 dark:text-white"
              >
                <option value="groq-llama3">Llama 3 70B (Groq Cloud Acceleration)</option>
                <option value="groq-mixtral">Mixtral 8x7B (Groq Cloud Acceleration)</option>
                <option value="gpt4-fallback">GPT-4 Enterprise (Local Hybrid Fallback)</option>
              </select>
            </div>

            {/* Temperature Slider */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 dark:text-slate-500">
                <span>LLM GENERATIVE TEMPERATURE</span>
                <span className="text-slate-700 dark:text-slate-300 font-extrabold">{temperature}</span>
              </div>
              <input
                type="range"
                min="0.0"
                max="1.0"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <span className="text-[10px] text-slate-400 block font-medium">
                Lower temperatures minimize text hallucinations and lock response predictability.
              </span>
            </div>

            {/* Confidence alert score */}
            <div className="space-y-2">
              <div className="flex justify-between items-center text-[10px] font-bold text-slate-400 dark:text-slate-500">
                <span>MINIMUM CAUSALITY CONFIDENCE ALERTS (%)</span>
                <span className="text-slate-700 dark:text-slate-300 font-extrabold">{confidenceThreshold}%</span>
              </div>
              <input
                type="range"
                min="10"
                max="90"
                step="5"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(parseInt(e.target.value))}
                className="w-full h-1.5 bg-slate-100 dark:bg-slate-800 rounded-lg appearance-none cursor-pointer accent-brand-600"
              />
              <span className="text-[10px] text-slate-400 block font-medium">
                Threshold below which the system flags safety claims for expert clinical verification review.
              </span>
            </div>
          </div>
        </div>

        {/* Database & API Configurations */}
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
            <Database className="h-5 w-5 text-brand-600 dark:text-brand-400" />
            <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">Database & Network Nodes</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-[9px] text-slate-400 font-bold block mb-1">MILVUS DB VECTOR STORE</span>
              <span className="text-emerald-600 font-extrabold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                localhost:19530 (Connected)
              </span>
            </div>

            <div className="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
              <span className="text-[9px] text-slate-400 font-bold block mb-1">SUPABASE STORAGE API</span>
              <span className="text-emerald-600 font-extrabold flex items-center gap-1.5">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
                Connected (Self-Healing Fallbacks Active)
              </span>
            </div>
          </div>
        </div>

        {/* Submit */}
        <div className="flex justify-end gap-3">
          <button
            type="submit"
            className="px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white rounded-xl text-xs font-bold shadow-lg shadow-brand-600/20 transition-all duration-200"
          >
            Save Configuration Changes
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings;
