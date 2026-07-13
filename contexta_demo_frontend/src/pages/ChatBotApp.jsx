import React, { useState, useEffect } from 'react';

import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';
import RightSidebar from '../components/RightSidebar';

export default function ChatBotApp() {
  const [showRightPanel, setShowRightPanel] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const initialMessage = { 
    id: 1, 
    text: "Hi Jay! 👋 \nI can help you book an appointment, find a doctor, or answer any questions you might have about our hospital. How can I assist you today?", 
    sender: 'bot', 
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
  };
  const [messages, setMessages] = useState([initialMessage]);

  const handleNewPatient = () => {
    setMessages([{ ...initialMessage, id: Date.now(), time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
  };

  useEffect(() => {
    return () => {
      document.documentElement.classList.remove('dark');
    };
  }, []);

  useEffect(() => {
    const isDark = localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches);
    setIsDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, []);

  const toggleTheme = () => {
    setIsDarkMode((prev) => {
      const newMode = !prev;
      localStorage.theme = newMode ? 'dark' : 'light';
      if (newMode) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
      return newMode;
    });
  };

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden font-sans bg-[#f7f7f7] dark:bg-[#202c33] text-[#111b21] dark:text-[#e9edef]">
      {/* Back to Home bar */}
      <div className="h-[44px] flex-shrink-0 bg-white dark:bg-[#111b21] border-b border-gray-200 dark:border-[#222e35] flex items-center px-4 z-20 transition-colors">
        <a 
          href="/" 
          className="flex items-center gap-2 text-sm font-semibold text-[#54656f] dark:text-[#aebac1] hover:text-[#00878A] dark:hover:text-[#00a884] transition-colors no-underline"
          onClick={() => document.documentElement.classList.remove('dark')}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Back to Home
        </a>
      </div>

      {/* Chat layout */}
      <div className="flex-1 flex overflow-hidden">
        <Sidebar 
          lastMessage={messages[messages.length - 1]} 
          isDarkMode={isDarkMode} 
          toggleTheme={toggleTheme} 
        />
        <ChatArea 
          messages={messages} 
          setMessages={setMessages} 
          onToggleInfo={() => setShowRightPanel(!showRightPanel)} 
          isDarkMode={isDarkMode}
          onNewPatient={handleNewPatient}
        />
        {showRightPanel && (
          <RightSidebar onClose={() => setShowRightPanel(false)} />
        )}
      </div>
    </div>
  );
}
