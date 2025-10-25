{/* Header */}
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import React,{useState} from "react";
export default function Header() {
    const [open, setOpen] = useState(false);
    return (
<header className="bg-blue-600 text-white px-6 py-3 flex items-center justify-between shadow-md font-inter">
  {/* 左侧：Logo + 应用名 */}
  <div className="flex items-center space-x-3">
    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center text-blue-600 font-bold text-lg">
      A
    </div>
    <h1 className="text-xl font-semibold tracking-wide">桌面语言助手</h1>
  </div>

  {/* 右侧：模块导航 */}
  <nav className="flex items-center space-x-4 ml-auto">
    {/* 语音聊天模块 */}
    <Link
      to="/chat"
      className="px-4 py-2 rounded-lg hover:bg-blue-500 transition-colors font-medium flex items-center space-x-1"
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 1v22M5 5l14 14" />
      </svg>
      <span>语音聊天</span>
    </Link>

    {/* 选择助手模块 */}
    <Link
      to="/system/assistants"
      className="px-4 py-2 rounded-lg hover:bg-blue-500 transition-colors font-medium flex items-center space-x-1"
    >
      <svg
        className="w-5 h-5"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v12m6-6H6" />
      </svg>
      <span>选择助手</span>
    </Link>

    <div className="relative">
      {/* 触发按钮 */}
      <button
        onClick={() => setOpen(!open)}
        className="px-4 py-2 rounded-lg hover:bg-blue-500 transition-colors font-medium w-full text-left flex justify-between items-center"
      >
        系统配置
        <svg
          className={`w-4 h-4 ml-2 transform transition-transform duration-200 ${
            open ? "rotate-180" : "rotate-0"
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>

      {/* 下拉菜单 */}
      {open && (
        <div className="absolute right-0 mt-2 w-44 bg-white text-black rounded-lg shadow-lg z-10">
          <Link to="/system/voice" className="block px-4 py-2 hover:bg-gray-100">
            声音设置
          </Link>
          <Link to="/system/model" className="block px-4 py-2 hover:bg-gray-100">
            模型设置
          </Link>
          <Link to="/system/chat" className="block px-4 py-2 hover:bg-gray-100">
            聊天配置
          </Link>
        </div>
      )}
    </div>
  </nav>
</header>)
}