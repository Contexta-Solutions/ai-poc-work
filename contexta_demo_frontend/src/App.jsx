import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import VisitNotesApp from './pages/VisitNotesApp';
import ChatBotApp from './pages/ChatBotApp';
import DoctorBotApp from './pages/DoctorBotApp';
import PasswordGate from './components/PasswordGate';
import { hasPass, onLocked } from './auth';

// Redirect to landing page on hard reload (Ctrl+R)
function RedirectOnReload() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // This only runs once on initial mount (page load / Ctrl+R).
    // SPA navigations don't remount this component.
    // Only a real reload redirects: the landing cards open each app in a new
    // tab, which is a fresh 'navigate' load and must land on its route.
    const isReload = performance.getEntriesByType('navigation')[0]?.type === 'reload';
    if (isReload && location.pathname !== '/') {
      navigate('/', { replace: true });
    }
  }, []);

  return null;
}

export default function App() {
  // Nothing renders, and no API call is made, until the backend has issued a
  // pass. A 401 from any call (expired pass, changed password) drops back here.
  const [unlocked, setUnlocked] = useState(hasPass);
  useEffect(() => onLocked(() => setUnlocked(false)), []);

  if (!unlocked) return <PasswordGate onUnlock={() => setUnlocked(true)} />;

  return (
    <BrowserRouter>
      <RedirectOnReload />
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/visit-notes" element={<VisitNotesApp />} />
        <Route path="/chatbot" element={<ChatBotApp />} />
        {/* Doctor-facing assistant over the patient chart. */}
        <Route path="/doctor" element={<DoctorBotApp />} />
      </Routes>
    </BrowserRouter>
  );
}