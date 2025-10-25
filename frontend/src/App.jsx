import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ChatPage from "./pages/ChatPage";
import ModelConfigPage from "./pages/ModelConfigPage";
import ChatConfigPage from "./pages/ChatConfigPage";
import SettingsPage from "./pages/SettingsPage";
import Header from "./components/Header";
import AssistantList from "./pages/assistant/AssistantList.jsx";
import AssistantEdit from "./pages/assistant/AssistantEdit.jsx";

function App() {
  return (
    <Router>
      <div className="flex flex-col min-h-screen bg-gray-100">
        <Header />
        <div className="flex-1 overflow-auto flex justify-center p-4">
          {/* 给页面内容一个最大宽度，让它不撑满整个屏幕 */}
          <div className="w-full max-w-5xl bg-white rounded-lg shadow-md p-6">
            <Routes>
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/chat/:sessionId" element={<ChatPage />} />
              <Route path="/model-config" element={<ModelConfigPage />} />
              <Route path="/chat-config" element={<ChatConfigPage />} />
              <Route path="/settings" element={<SettingsPage />} />

              {/* ✅ 语音配置页面 */}

              <Route path="/system/assistants" element={<AssistantList />} />
              <Route path="/system/assistants/new" element={<AssistantEdit />} />
              <Route path="/system/assistants/:id/edit" element={<AssistantEdit />} />
              {/* 默认跳转 */}
              <Route path="*" element={<ChatPage />} />
            </Routes>
          </div>
        </div>
      </div>
    </Router>
  );
}
export default App;