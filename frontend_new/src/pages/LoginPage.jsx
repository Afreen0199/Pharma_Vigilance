import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ShieldCheck, Mail, Lock, Loader2, Activity, Shield } from 'lucide-react';

const LoginPage = () => {
  const { login, register } = useAuth();
  const navigate = useNavigate();

  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');

    if (!email || !password) {
      setError('Please fill in all required fields.');
      return;
    }

    if (!isLogin && password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      if (isLogin) {
        const res = await login(email, password);
        if (res.success) {
          navigate('/');
        } else {
          setError(res.error || 'Login failed.');
        }
      } else {
        const res = await register(email, password);
        if (res.success) {
          setSuccessMsg('Account registered successfully. You can now log in.');
          setIsLogin(true);
          setPassword('');
          setConfirmPassword('');
        } else {
          setError(res.error || 'Registration failed.');
        }
      }
    } catch (err) {
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex min-h-screen bg-slate-50 dark:bg-slate-950">
      {/* Left side: Branding / Visuals (Hidden on mobile, takes 50% on desktop) */}
      <div className="hidden lg:flex lg:w-1/2 relative bg-slate-900 overflow-hidden items-center justify-center p-12">
        {/* Decorative background elements */}
        <div className="absolute top-[-20%] left-[-10%] w-[70%] h-[70%] rounded-full bg-violet-600/20 blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-[-20%] right-[-10%] w-[70%] h-[70%] rounded-full bg-emerald-600/20 blur-[120px] pointer-events-none"></div>
        
        {/* Grid pattern overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iMjAiIGN5PSIyMCIgcj0iMSIgZmlsbD0icmdiYSgyNTUsIDI1NSwgMjU1LCAwLjA1KSIvPjwvc3ZnPg==')] opacity-50"></div>

        <div className="relative z-10 w-full max-w-lg text-white">
          <div className="inline-flex p-4 bg-white/10 backdrop-blur-xl rounded-2xl mb-8 border border-white/10 shadow-2xl">
            <Shield className="h-12 w-12 text-violet-400" />
          </div>
          
          <h1 className="text-4xl lg:text-5xl font-bold tracking-tight mb-6">
            Safety Intelligence
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-emerald-400 mt-2">
              Pharmacovigilance Platform
            </span>
          </h1>
          
          <p className="text-lg text-slate-300 mb-10 leading-relaxed max-w-md">
            AI-powered safety signal detection, verification, and automated reporting for the modern pharmaceutical enterprise.
          </p>

          <div className="grid grid-cols-2 gap-4 text-sm font-medium text-slate-400">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/5 rounded-lg border border-white/5"><Activity className="h-5 w-5 text-violet-400"/></div>
              <span>Real-time Monitoring</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/5 rounded-lg border border-white/5"><ShieldCheck className="h-5 w-5 text-emerald-400"/></div>
              <span>Evidence Verification</span>
            </div>
          </div>
        </div>
      </div>

      {/* Right side: Form (Takes full width on mobile, 50% on desktop) */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 relative">
        {/* Mobile background glows (only visible on mobile) */}
        <div className="absolute top-0 right-0 w-[50%] h-[50%] rounded-full bg-violet-500/5 blur-[100px] pointer-events-none lg:hidden"></div>

        <div className="w-full max-w-md space-y-8 relative z-10">
          <div className="text-center lg:text-left space-y-2 mb-8">
            <div className="lg:hidden inline-flex p-3 bg-violet-600 rounded-xl text-white mb-4 shadow-lg shadow-violet-600/20">
              <Shield className="h-8 w-8" />
            </div>
            <h2 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              Welcome back
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Sign in to your AI Pharmacovigilance Copilot
            </p>
          </div>

          <div className="bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 p-8 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-none space-y-6 backdrop-blur-xl">
            {/* Tabs */}
            <div className="flex bg-slate-100 dark:bg-slate-950 p-1.5 rounded-2xl">
              <button
                onClick={() => {
                  setIsLogin(true);
                  setError('');
                  setSuccessMsg('');
                }}
                className={`flex-1 text-center py-2.5 text-sm font-semibold rounded-xl transition-all duration-200 cursor-pointer ${
                  isLogin 
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                }`}
              >
                Sign In
              </button>
              <button
                onClick={() => {
                  setIsLogin(false);
                  setError('');
                  setSuccessMsg('');
                }}
                className={`flex-1 text-center py-2.5 text-sm font-semibold rounded-xl transition-all duration-200 cursor-pointer ${
                  !isLogin 
                    ? 'bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm' 
                    : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-300'
                }`}
              >
                Register
              </button>
            </div>

            {error && (
              <div className="p-4 bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 rounded-2xl text-sm font-medium text-red-600 dark:text-red-400 flex items-start gap-3">
                <div className="mt-0.5"><Activity className="h-4 w-4" /></div>
                {error}
              </div>
            )}

            {successMsg && (
              <div className="p-4 bg-emerald-50 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20 rounded-2xl text-sm font-medium text-emerald-600 dark:text-emerald-400 flex items-start gap-3">
                <div className="mt-0.5"><ShieldCheck className="h-4 w-4" /></div>
                {successMsg}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email Address */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block">
                  Email Address
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-violet-500 transition-colors">
                    <Mail className="h-5 w-5" />
                  </div>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="reviewer@organization.com"
                    className="block w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 dark:focus:border-violet-500 font-medium text-slate-900 dark:text-white transition-all"
                  />
                </div>
              </div>

              {/* Password */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block">
                  Password
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-violet-500 transition-colors">
                    <Lock className="h-5 w-5" />
                  </div>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="block w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 dark:focus:border-violet-500 font-medium text-slate-900 dark:text-white transition-all"
                  />
                </div>
              </div>

              {/* Confirm Password (register mode only) */}
              {!isLogin && (
                <div className="space-y-1.5 animate-in slide-in-from-top-2 fade-in duration-200">
                  <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block">
                    Confirm Password
                  </label>
                  <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400 group-focus-within:text-violet-500 transition-colors">
                      <Lock className="h-5 w-5" />
                    </div>
                    <input
                      type="password"
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      className="block w-full pl-11 pr-4 py-3 bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 rounded-2xl text-sm placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 dark:focus:border-violet-500 font-medium text-slate-900 dark:text-white transition-all"
                    />
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full flex items-center justify-center gap-2 py-3 bg-violet-600 hover:bg-violet-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white rounded-2xl text-sm font-bold shadow-lg shadow-violet-600/30 hover:shadow-xl hover:shadow-violet-600/40 transition-all duration-200 mt-8 cursor-pointer transform hover:-translate-y-0.5 active:translate-y-0"
              >
                {loading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>{isLogin ? 'Sign In to Workspace' : 'Create Access Account'}</span>
                )}
              </button>
            </form>
          </div>
          
          <div className="text-center">
            <p className="text-xs text-slate-500 dark:text-slate-500">
              By signing in, you agree to our Terms of Service and Privacy Policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
