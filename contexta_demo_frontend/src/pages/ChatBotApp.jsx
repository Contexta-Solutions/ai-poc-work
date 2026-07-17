import React, { useState, useEffect } from 'react';

import Sidebar from '../components/Sidebar';
import ChatArea from '../components/ChatArea';
import RightSidebar from '../components/RightSidebar';

export default function ChatBotApp() {
  const [showRightPanel, setShowRightPanel] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  // Only one pane fits on a phone, so we show either the chat list or the
  // conversation -- like WhatsApp. Land on the conversation: there's only one
  // chat here, so making the user tap through a list first is pure friction.
  // From `md` up both panes are on screen at once and this is ignored.
  const [mobileView, setMobileView] = useState('chat'); // 'chat' | 'list'
  const initialMessage = {
    id: 1,
    text: "Hi Jay! 👋 Welcome to OrthoCare Clinic.\n\nI can help you with:\n📅 Book a doctor appointment\n📍 Clinic locations & addresses\n🕐 Doctor availability & timings\n🩻 Lab & scan info and booking numbers (X-ray, Blood work, Ultrasound, MRI, CT)\n☎️ Contact person & phone for each branch\n\nJust let me know what you're looking for!",
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
    // 100dvh, not 100vh: on mobile browsers 100vh includes the address bar, so
    // the composer ends up pushed below the fold.
    <div className="h-[100dvh] w-full flex flex-col overflow-hidden font-sans bg-[#f7f7f7] dark:bg-[#202c33] text-[#111b21] dark:text-[#e9edef]">
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

      {/* Chat layout.
          phone (<md): one pane at a time -- chat list OR conversation, full width.
          tablet (md-lg): two panes, list + conversation.
          desktop (lg+): three panes, doctor directory sits inline as a column. */}
      <div className="flex-1 flex overflow-hidden relative">
        <Sidebar
          className={`${mobileView === 'list' ? 'flex' : 'hidden'} md:flex w-full md:w-[35%] md:min-w-[280px] md:max-w-[400px]`}
          lastMessage={messages[messages.length - 1]}
          isDarkMode={isDarkMode}
          toggleTheme={toggleTheme}
          onSelectChat={() => setMobileView('chat')}
        />
        <ChatArea
          className={`${mobileView === 'chat' ? 'flex' : 'hidden'} md:flex`}
          messages={messages}
          setMessages={setMessages}
          onToggleInfo={() => setShowRightPanel(!showRightPanel)}
          isDarkMode={isDarkMode}
          onNewPatient={handleNewPatient}
          onBack={() => setMobileView('list')}
        />
        {showRightPanel && (
          // Below lg it covers the conversation entirely (like WhatsApp's
          // Contact Info screen); at lg+ it becomes a normal third column.
          <RightSidebar
            onClose={() => setShowRightPanel(false)}
            className="absolute inset-0 z-30 w-full lg:static lg:z-auto lg:w-[30%] lg:min-w-[320px] lg:max-w-[400px]"
          />
        )}
      </div>
    </div>
  );
}
