import { useEffect, useRef, useState } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { ContextaLogo } from '../pages/LandingPage';
import { getTries, login, MAX_TRIES } from '../auth';

const mmss = (ms) => {
  const s = Math.max(0, Math.ceil(ms / 1000));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;
};

// Full-screen password screen shown in place of the whole app until the
// backend hands out a pass. Styled to match the landing page.
export default function PasswordGate({ onUnlock }) {
  const [password, setPassword] = useState('');
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [tries, setTries] = useState(getTries);
  const [now, setNow] = useState(Date.now);
  const inputRef = useRef(null);

  const locked = tries.lockedUntil > now;

  // Tick while locked so the countdown moves; it stops itself on unlock.
  useEffect(() => {
    if (!locked) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [locked]);

  // Focus on load and again when a lockout ends (the input was disabled).
  useEffect(() => {
    if (!locked) inputRef.current?.focus();
  }, [locked]);

  const submit = async (e) => {
    e.preventDefault();
    if (!password || busy || locked) return;
    setBusy(true);
    const result = await login(password);
    setBusy(false);
    if (result.ok) return onUnlock();
    setTries(result.tries);
    setNow(Date.now());
    setError(result.error || '');
    setPassword('');
    inputRef.current?.focus();
  };

  const left = MAX_TRIES - tries.fails;
  const message = locked
    ? `Too many wrong tries. Try again in ${mmss(tries.lockedUntil - now)}.`
    : error || (tries.fails > 0 ? `Wrong password. ${left} ${left === 1 ? 'try' : 'tries'} left.` : '');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-teal-50/30 flex flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-sm">
        <div className="flex justify-center mb-8">
          <ContextaLogo className="h-[30px] w-auto" />
        </div>

        <form
          onSubmit={submit}
          className="bg-white/70 backdrop-blur-xl rounded-[2rem] p-6 sm:p-8 border border-white shadow-[0_8px_30px_rgb(0,0,0,0.06)]"
        >
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">This demo is private</h1>
          <p className="text-slate-500 text-[15px] mt-1.5 mb-6">Enter the team password to continue.</p>

          <label htmlFor="demo-password" className="block text-sm font-semibold text-slate-700 mb-2">
            Password
          </label>
          <div className="relative">
            <input
              id="demo-password"
              ref={inputRef}
              type={show ? 'text' : 'password'}
              value={password}
              onChange={(e) => { setPassword(e.target.value); setError(''); }}
              disabled={locked || busy}
              autoComplete="current-password"
              aria-invalid={Boolean(message)}
              aria-describedby="gate-message"
              className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 pr-12 text-[15px] text-slate-800 outline-none transition focus:border-teal-500 focus:ring-4 focus:ring-teal-500/15 disabled:bg-slate-50 disabled:text-slate-400"
            />
            <button
              type="button"
              onClick={() => setShow((s) => !s)}
              aria-label={show ? 'Hide password' : 'Show password'}
              aria-pressed={show}
              className="absolute inset-y-0 right-0 flex items-center px-4 text-slate-400 hover:text-slate-600 transition-colors"
            >
              {show ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>

          <p id="gate-message" role="status" aria-live="polite" className="min-h-[20px] mt-3 text-sm font-medium text-rose-600">
            {message}
          </p>

          <button
            type="submit"
            disabled={!password || busy || locked}
            className="mt-3 w-full rounded-xl bg-gradient-to-r from-teal-600 to-emerald-600 py-3 text-[15px] font-semibold text-white shadow-lg shadow-teal-600/20 transition hover:from-teal-700 hover:to-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? 'Checking…' : locked ? 'Locked' : 'Unlock'}
          </button>
        </form>

        <p className="text-center text-xs text-slate-400 mt-6">Don't have the password? Ask the Contexta team.</p>
      </div>
    </div>
  );
}
