import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, Square, CheckCheck, Stethoscope, UserPlus, ArrowLeft } from 'lucide-react';

const formatMessage = (text) => {
  if (!text) return null;
  
  let cleanText = text
    .replace(/\|/g, '')
    .replace(/---/g, '')
    .replace(/(^|\n)(#+ |> )/g, '$1');

  const parts = cleanText.split(/(\*\*.*?\*\*)/g);
  return parts.map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-[#111b21] dark:text-white">{part.slice(2, -2)}</strong>;
    }
    return <React.Fragment key={index}>{part}</React.Fragment>;
  });
};

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.VITE_API_URL || '';

// Tappable starter prompts shown on a fresh conversation. `label` is what the
// patient sees; `text` is the actual message sent to the bot.
const QUICK_REPLIES = [
  { label: '📅 Book appointment', text: 'I want to book an appointment' },
  { label: '📍 Locations', text: 'What are your clinic locations and addresses?' },
  { label: '🕐 Doctor timings', text: 'Show me the doctors and their availability' },
  { label: '🩻 Lab & scan timings', text: 'What are the lab and scan (X-ray, MRI, CT) timings?' },
  { label: '📋 My appointment', text: 'What appointments do I have booked?' },
];

export default function ChatArea({ messages, setMessages, onToggleInfo, isDarkMode, onNewPatient, className = '', onBack }) {
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessingAudio, setIsProcessingAudio] = useState(false);
  const [isBotTyping, setIsBotTyping] = useState(false);

  const messagesEndRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const textareaRef = useRef(null);
  const justTranscribedRef = useRef(false);
  // Language Whisper heard on the last voice message ("en" / "te"). Sent along
  // with the chat request so the assistant answers in the language the patient
  // actually spoke, instead of guessing from the text. Sticks until the next
  // voice message changes it; null for a text-only conversation.
  const detectedLanguageRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isBotTyping]);

  // Focus textarea after transcription completes and textarea is re-enabled
  useEffect(() => {
    if (!isProcessingAudio && justTranscribedRef.current) {
      justTranscribedRef.current = false;
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
      // Auto-send the transcribed message
      handleSend();
    }
  }, [isProcessingAudio]);

  const handleSend = async (overrideText) => {
    // overrideText comes from a quick-reply chip; a click event (from the send
    // button) isn't a string, so it falls back to the typed input.
    const userText = (typeof overrideText === 'string' ? overrideText : inputValue).trim();
    if (!userText) return;

    const newUserMsg = {
      id: Date.now(), text: userText, sender: 'user',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    const historyPayload = messages.map(msg => ({
      role: msg.sender,
      content: msg.text
    }));

    setMessages(prev => [...prev, newUserMsg]);
    setInputValue('');

    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    setIsBotTyping(true);
    try {
      const response = await fetch(`${BACKEND_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userText,
          history: historyPayload,
          language: detectedLanguageRef.current
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unknown server error");
      }

      setMessages(prev => [...prev, {
        id: Date.now() + 1, text: data.reply, sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } catch (error) {
      console.error("Backend error:", error);
      setMessages(prev => [...prev, {
        id: Date.now() + 1, text: ` System Error: ${error.message}`, sender: 'bot',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }]);
    } finally {
      setIsBotTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e) => {
    setInputValue(e.target.value);
    e.target.style.height = 'auto';
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        setIsProcessingAudio(true);
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append("file", audioBlob, "audio.webm");
        // No `language` field: let Whisper auto-detect so the patient can speak
        // English or Telugu without setting anything. The backend tells us which
        // it heard. (Transcription goes through the backend rather than straight
        // to Groq, so the API key never ships to the browser.)

        try {
          const res = await fetch(`${BACKEND_URL}/api/transcribe`, {
            method: "POST",
            body: formData
          });

          if (!res.ok) {
            let detail = `Transcription failed (${res.status})`;
            try {
              const err = await res.json();
              detail = err.detail || detail;
            } catch {
              // response wasn't JSON; keep the status-code message
            }
            throw new Error(detail);
          }

          const data = await res.json();

          // null when Whisper heard something that isn't English or Telugu --
          // keep whatever language the conversation was already in.
          if (data.language) {
            detectedLanguageRef.current = data.language;
          }

          if (data.text && data.text.trim()) {
            setInputValue(prev => prev + (prev ? " " : "") + data.text.trim());
            justTranscribedRef.current = true;
            if (textareaRef.current) {
              setTimeout(() => {
                textareaRef.current.style.height = 'auto';
                textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
              }, 0);
            }
          }
        } catch (error) {
          console.error("Transcription error:", error);
          setMessages(prev => [...prev, {
            id: Date.now(), text: ` Sorry, I couldn't hear that — please try again or type your message.`, sender: 'bot',
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }]);
        } finally {
          setIsProcessingAudio(false);
          stream.getTracks().forEach(track => track.stop());
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Microphone access denied:", err);
      alert("Please allow microphone access to use voice typing.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <div className={`${className} flex-1 flex-col bg-[#efeae2] dark:bg-[#0b141a] relative min-w-0 transition-colors`}>
      <div
        className={`absolute inset-0 z-0 pointer-events-none ${isDarkMode ? 'opacity-[0.04] invert' : 'opacity-[0.06]'}`}
        style={{ backgroundImage: 'url("https://static.whatsapp.net/rsrc.php/v3/yl/r/gi_DckOUM5a.png")' }}
      ></div>

      <div className="h-[60px] flex-shrink-0 bg-white dark:bg-[#111b21] flex items-center justify-between px-2 sm:px-4 z-10 border-b border-gray-200 dark:border-[#202c33] transition-colors">
        {/* Back to the chat list -- phone only; from md up the list is already on screen. */}
        <button
          onClick={onBack}
          className="md:hidden p-1.5 rounded-md text-[#54656f] dark:text-[#aebac1] hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors flex-shrink-0"
          title="Back to chats"
        >
          <ArrowLeft size={22} />
        </button>
        <div className="flex items-center cursor-pointer flex-1 min-w-0 group" onClick={onToggleInfo}>
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-full flex items-center justify-center bg-[#00a884] dark:bg-[#00a884] overflow-hidden flex-shrink-0">
            <img src="/favicon.svg" alt="Contexta Health" className="w-full h-full object-cover" />
          </div>
          <div className="ml-2 sm:ml-4 min-w-0">
            <h2 className="text-[15px] sm:text-[16px] text-[#111b21] dark:text-[#e9edef] font-medium group-hover:underline truncate">Contexta Health</h2>
            <p className="text-[12px] sm:text-[13px] text-[#667781] dark:text-[#8696a0] truncate">AI Clinical Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-0.5 sm:gap-2 text-[#54656f] dark:text-[#aebac1] flex-shrink-0">
          <button
            className="flex items-center gap-1.5 px-2 sm:px-3 py-1.5 rounded-md text-sm font-medium hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors border border-transparent hover:border-gray-200 dark:hover:border-[#2a3942]"
            onClick={onNewPatient}
            title="Start New Patient Session"
          >
            <UserPlus size={18} />
            <span className="hidden lg:inline">New Patient</span>
          </button>
          <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors" onClick={onToggleInfo} title="View Doctor List">
            <Stethoscope size={22} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden px-3 sm:px-[5%] lg:px-[10%] py-4 z-10 flex flex-col gap-2">
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`px-3 py-2 max-w-[85%] sm:max-w-[75%] shadow-sm relative text-[14.2px] rounded-lg ${
                msg.sender === 'user'
                  ? 'bg-[#d9fdd3] dark:bg-[#005c4b] text-[#111b21] dark:text-[#e9edef] rounded-tr-none'
                  : 'bg-white dark:bg-[#202c33] text-[#111b21] dark:text-[#e9edef] rounded-tl-none'
              }`}
            >
              <span className="whitespace-pre-wrap break-words leading-relaxed">{formatMessage(msg.text)}</span>
              <div className="text-[11px] text-[#667781] dark:text-[#8696a0] text-right mt-1 ml-3 inline-flex items-center float-right gap-1">
                {msg.time}
                {msg.sender === 'user' && (
                  <CheckCheck size={15} className="text-[#53bdeb]" />
                )}
              </div>
            </div>
          </div>
        ))}

        {isBotTyping && (
          <div className="flex justify-start">
            <div className="px-3.5 py-3 bg-white dark:bg-[#202c33] rounded-lg rounded-tl-none shadow-sm">
              <div className="flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-[#8696a0] animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-[#8696a0] animate-bounce" style={{ animationDelay: '150ms' }} />
                <span className="w-1.5 h-1.5 rounded-full bg-[#8696a0] animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick-reply starter chips -- only on a fresh chat, to nudge the patient. */}
      {messages.length <= 1 && !isRecording && !isProcessingAudio && !isBotTyping && (
        <div className="z-10 flex-shrink-0 flex gap-2 overflow-x-auto px-2 sm:px-4 pb-1 pt-1 no-scrollbar">
          {QUICK_REPLIES.map((q) => (
            <button
              key={q.label}
              onClick={() => handleSend(q.text)}
              className="whitespace-nowrap flex-shrink-0 text-[13px] px-3 py-1.5 rounded-full border border-[#00a884]/40 text-[#008069] dark:text-[#46c2a8] bg-white dark:bg-[#202c33] hover:bg-[#f0f2f5] dark:hover:bg-[#2a3942] transition-colors shadow-sm"
            >
              {q.label}
            </button>
          ))}
        </div>
      )}

      <div className="bg-[#f0f2f5] dark:bg-[#202c33] flex-shrink-0 flex items-end px-2 sm:px-4 py-2 sm:py-3 z-10 transition-colors">
        <div className="flex-1 min-w-0 bg-white dark:bg-[#2a3942] rounded-lg flex items-center px-3 shadow-sm py-2 transition-colors border border-transparent focus-within:border-gray-300 dark:focus-within:border-gray-600">
          <textarea 
            ref={textareaRef}
            rows={1}
            placeholder={isProcessingAudio ? "Transcribing..." : isRecording ? "Listening..." : "Type a message"} 
            value={inputValue}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            disabled={isRecording || isProcessingAudio}
            /* 16px on phones: iOS Safari zooms the whole page in when you focus
               an input with a smaller font size. */
            className="w-full bg-transparent border-none outline-none focus-visible:outline-none text-[16px] sm:text-[15px] text-[#111b21] dark:text-[#e9edef] placeholder-[#667781] dark:placeholder-[#8696a0] resize-none overflow-y-auto min-h-[24px] max-h-[120px]"
          />
        </div>

        <div className="flex items-center justify-center ml-2 sm:ml-4 pb-2 flex-shrink-0 text-[#54656f] dark:text-[#aebac1]">
          {inputValue.trim() ? (
             <button onClick={handleSend} className="hover:text-[#00a884] transition">
               <Send size={24} />
             </button>
          ) : (
            <button 
              onClick={isRecording ? stopRecording : startRecording} 
              className={`transition rounded-full ${isRecording ? 'text-red-500 animate-pulse' : 'hover:text-[#00a884]'}`}
              disabled={isProcessingAudio}
            >
              {isRecording ? <Square size={20} fill="currentColor" /> : <Mic size={24} />}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
