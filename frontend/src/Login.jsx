import React, { useState } from 'react';
import { ChefHat, Lock, User, Loader2 } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const res = await fetch(`${API}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Invalid credentials');
      }

      const data = await res.json();
      onLogin(data.access_token);
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center items-center p-6 text-slate-800" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
      <div className="w-full max-w-md bg-white rounded-3xl shadow-xl border border-slate-100 p-8 space-y-8">
        <div className="text-center">
          <div className="bg-rose-600 text-white w-20 h-20 rounded-2xl flex items-center justify-center mx-auto shadow-lg mb-6 shadow-rose-200">
            <ChefHat className="w-10 h-10" />
          </div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">Meatcraft Admin</h1>
          <p className="text-sm text-slate-500 font-medium">Please sign in to access the dashboard</p>
        </div>

        {error && (
          <div className="bg-rose-50 text-rose-600 text-sm font-bold p-4 rounded-xl border border-rose-100 text-center">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                <User className="h-5 w-5" />
              </div>
              <input
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="block w-full pl-11 pr-4 py-4 border-2 border-slate-100 rounded-2xl text-sm font-medium text-slate-800 focus:ring-0 focus:border-rose-500 focus:outline-none transition-colors bg-slate-50 focus:bg-white"
                placeholder="Username"
              />
            </div>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
                <Lock className="h-5 w-5" />
              </div>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-11 pr-4 py-4 border-2 border-slate-100 rounded-2xl text-sm font-medium text-slate-800 focus:ring-0 focus:border-rose-500 focus:outline-none transition-colors bg-slate-50 focus:bg-white"
                placeholder="Password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex justify-center items-center py-4 px-4 border border-transparent rounded-2xl shadow-sm text-sm font-bold text-white bg-rose-600 hover:bg-rose-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-rose-500 transition-all disabled:opacity-70 active:scale-95"
          >
            {loading ? <Loader2 className="animate-spin h-5 w-5" /> : 'Sign In'}
          </button>
        </form>
      </div>
      <p className="mt-8 text-xs text-slate-400 font-medium text-center">
        Secure centralized access for the Meatcraft shop team.
      </p>
    </div>
  );
}
