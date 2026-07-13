import React from 'react';
import { Search, MoreHorizontal, Edit, Moon, Sun, User } from 'lucide-react';

export default function Sidebar({ lastMessage, isDarkMode, toggleTheme }) {
  return (
    <div className="w-[30%] min-w-[320px] max-w-[400px] border-r border-gray-200 dark:border-[#222e35] flex flex-col bg-white dark:bg-[#111b21] overflow-hidden transition-colors">
      
      <div className="h-[60px] flex items-center justify-between px-4 mt-2 flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Default Anonymous User PFP */}
          <div className="w-8 h-8 rounded-full bg-[#dfe5e7] dark:bg-[#6c7175] flex items-center justify-center overflow-hidden flex-shrink-0">
            <User size={24} className="text-[#a6b0b5] dark:text-[#d1d7db] mt-1.5" fill="currentColor" />
          </div>
          <h1 className="text-2xl font-bold text-[#111b21] dark:text-[#e9edef]">Chats</h1>
        </div>
        
        <div className="flex items-center gap-3 text-[#54656f] dark:text-[#aebac1]">
          <button onClick={toggleTheme} className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors" title="Toggle Theme">
            {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
          <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors">
            <Edit size={20} />
          </button>
          <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#202c33] transition-colors">
            <MoreHorizontal size={20} />
          </button>
        </div>
      </div>

      <div className="px-3 pb-2 pt-1 flex-shrink-0">
        <div className="bg-[#f0f2f5] dark:bg-[#202c33] flex items-center px-3 py-1.5 rounded-md border-b-2 border-transparent focus-within:border-[#00a884] transition-all">
          <Search size={18} className="text-[#54656f] dark:text-[#8696a0]" />
          <input 
            type="text" 
            placeholder="Search or start new chat" 
            className="w-full bg-transparent border-none outline-none ml-3 text-[14px] text-[#111b21] dark:text-[#e9edef] placeholder-[#54656f] dark:placeholder-[#8696a0]"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden">
        <div className="flex items-center px-3 py-3 bg-[#f5f6f6] dark:bg-[#2a3942] cursor-pointer hover:bg-[#f0f2f5] dark:hover:bg-[#202c33] transition-colors rounded-lg mx-2 my-1">
          {/* Fixed Logo Padding */}
          <div className="w-12 h-12 rounded-full overflow-hidden flex items-center justify-center bg-[#00a884] dark:bg-[#00a884] flex-shrink-0">
            <img src="/favicon.svg" alt="Contexta Health" className="w-full h-full object-cover" />
          </div>
          <div className="ml-3 flex-1 min-w-0">
            <div className="flex justify-between items-center">
              <h2 className="text-[16px] text-[#111b21] dark:text-[#e9edef] font-medium truncate">Contexta Health</h2>
              <span className="text-[12px] text-[#667781] dark:text-[#8696a0] flex-shrink-0 ml-2">{lastMessage?.time}</span>
            </div>
            <div className="text-[13px] text-[#667781] dark:text-[#8696a0] truncate mt-0.5">
              {lastMessage?.sender === 'user' ? 'You: ' : ''}{lastMessage?.text}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
