import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import VisitNotesApp from './pages/VisitNotesApp';
import ChatBotApp from './pages/ChatBotApp';
import DoctorBotApp from './pages/DoctorBotApp';

// Redirect to landing page on hard reload (Ctrl+R)
function RedirectOnReload() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // This only runs once on initial mount (page load / Ctrl+R).
    // SPA navigations don't remount this component.
    if (location.pathname !== '/') {
      navigate('/', { replace: true });
    }
  }, []);

  return null;
}

export default function App() {
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