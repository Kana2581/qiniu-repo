import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiFetch } from "../../utils/api.js";

export default function AssistantEdit() {
  const { id } = useParams();
  const navigate = useNavigate();

  const PROVIDERS = ["Ollama", "OpenAI", "Gemini"]; // 下拉选项
  const AVATARS = ["🤖", "🧑‍💻", "👩‍🏫", "🧙‍♂️", "🐱", "🐶", "🦄", "🦖"]; // emoji头像选择

const [form, setForm] = useState({
  name: "",
  base_url: "",
  provider: "",
  model_name: "",
  api_key: "",
  description: "",
  avatar: AVATARS[0],
  prompt_text: "你是一个助手",
  window_size: 30,
  voice_name: "",
  voice_type: "",
  speed_ratio: 1.0,
  system_type: "",
  base_file_path: "",
});


  const [voices, setVoices] = useState([]);
  const [loadingVoices, setLoadingVoices] = useState(true);
  const [loadingForm, setLoadingForm] = useState(!!id);
  const [errors, setErrors] = useState({});

  // 加载语音列表
  useEffect(() => {
    fetch("https://openai.qiniu.com/v1/voice/list")
      .then((res) => res.json())
      .then((data) => setVoices(data))
      .catch((err) => console.error("语音类型加载失败：", err))
      .finally(() => setLoadingVoices(false));
  }, []);

  // 编辑模式，加载表单数据
  useEffect(() => {
    if (!id) return;
    setLoadingForm(true);
    apiFetch(`/assistants/${id}`)
      .then((res) => res.json())
      .then((data) => setForm({ ...form, ...data }))
      .catch((err) => console.error("加载助手配置失败：", err))
      .finally(() => setLoadingForm(false));
  }, [id]);

  const handleChange = (e) => {
    let value =
      e.target.type === "number" ? parseFloat(e.target.value) : e.target.value;

    if (e.target.name === "name" && value.length > 100) value = value.slice(0, 100);
    if (e.target.name === "provider" && value.length > 100) value = value.slice(0, 100);
    if (e.target.name === "model_name" && value.length > 100) value = value.slice(0, 100);
    if (e.target.name === "api_key" && value.length > 255) value = value.slice(0, 255);
    if (e.target.name === "voice_type" && value.length > 100) value = value.slice(0, 100);

    if (e.target.name === "speed_ratio") {
      if (value < 0.5) value = 0.5;
      if (value > 3.0) value = 3.0;
      value = Number(value.toFixed(2));
    }

    if (e.target.name === "window_size") {
      if (value < 1) value = 1;
      if (value > 100) value = 100;
    }

    setForm({ ...form, [e.target.name]: value });
    setErrors({ ...errors, [e.target.name]: "" });
  };

  const validateForm = () => {
    const newErrors = {};
    if (!form.name.trim()) newErrors.name = "名称不能为空";
    if (!form.provider.trim()) newErrors.provider = "提供商不能为空";
    if (!form.model_name.trim()) newErrors.model_name = "模型名称不能为空";
    if (!form.voice_name.trim()) newErrors.voice_name = "语音不能为空";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const method = id ? "PUT" : "POST";
    const url = id ? `/assistants/${id}` : "/assistants";

    try {
      const res = await apiFetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const result = await res.json();
      alert(result.message || "保存成功");
      navigate("/system/assistants");
    } catch (err) {
      console.error("保存失败：", err);
      alert("保存失败，请重试");
    }
  };

  if (loadingVoices || loadingForm)
    return <div className="p-6">正在加载...</div>;

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <h2 className="text-2xl font-semibold text-center mb-4">
        {id ? "编辑助手配置" : "新增助手配置"}
      </h2>

      {/* 基本信息卡 */}
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-medium border-b pb-2 mb-4">基本信息</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block mb-1 font-medium">助手名称</label>
            <input
              name="name"
              value={form.name}
              onChange={handleChange}
              className={`w-full border rounded px-3 py-2 ${errors.name ? "border-red-500" : ""}`}
              required
            />
            {errors.name && <p className="text-red-500 text-sm mt-1">{errors.name}</p>}
          </div>

          <div>
            <label className="block mb-1 font-medium">窗口大小</label>
            <input
              name="window_size"
              type="number"
              value={form.window_size}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
              required
            />
          </div>

          <div className="md:col-span-2">
            <label className="block mb-1 font-medium">描述</label>
            <input
              name="description"
              value={form.description}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
            />
          </div>

          <div className="md:col-span-2">
            <label className="block mb-1 font-medium">提示文本</label>
            <textarea
              name="prompt_text"
              value={form.prompt_text}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
            />
          </div>
        </div>
      </div>

      {/* 模型配置卡 */}
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-medium border-b pb-2 mb-4">模型配置</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Emoji头像选择 */}
          <div className="md:col-span-2 mt-4">
            <label className="block mb-2 font-medium">选择头像</label>
            <div className="grid grid-cols-8 gap-2">
              {AVATARS.map((av) => (
                <button
                  key={av}
                  type="button"
                  className={`text-2xl py-2 border rounded-lg ${
                    form.avatar === av ? "border-blue-500 bg-blue-100" : "border-gray-300"
                  }`}
                  onClick={() => setForm({ ...form, avatar: av })}
                >
                  {av}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block mb-1 font-medium">提供商</label>
            <select
              name="provider"
              value={form.provider}
              onChange={handleChange}
              className={`w-full border rounded px-3 py-2 ${errors.provider ? "border-red-500" : ""}`}
            >
              <option value="">请选择提供商</option>
              {PROVIDERS.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
            {errors.provider && <p className="text-red-500 text-sm mt-1">{errors.provider}</p>}
          </div>

          <div>
            <label className="block mb-1 font-medium">模型名称</label>
            <input
              name="model_name"
              value={form.model_name}
              onChange={handleChange}
              className={`w-full border rounded px-3 py-2 ${errors.model_name ? "border-red-500" : ""}`}
              required
            />
            {errors.model_name && <p className="text-red-500 text-sm mt-1">{errors.model_name}</p>}
          </div>

          <div>
            <label className="block mb-1 font-medium">API Key</label>
            <input
              name="api_key"
              value={form.api_key}
              onChange={handleChange}
              className={`w-full border rounded px-3 py-2 ${errors.api_key ? "border-red-500" : ""}`}
 
            />
           
          </div>
                    <div>
            <label className="block mb-1 font-medium">基础 URL</label>
            <input
              name="base_url"
              value={form.base_url}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
            />
          </div>


        </div>
      </div>

      {/* 声音配置卡 */}
      <div className="bg-white shadow-md rounded-lg p-6 space-y-4">
        <h3 className="text-xl font-medium border-b pb-2 mb-4">声音配置</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block mb-1 font-medium">语音选择</label>
          <select
            name="voice_name"
            value={form.voice_name}
            onChange={(e) => {
              const selected = voices.find(v => v.voice_name === e.target.value);
              setForm({
                ...form,
                voice_name: selected?.voice_name || "",
                voice_type: selected?.voice_type || "",
              });
              setErrors({ ...errors, voice_name: "" });
            }}
            className={`w-full border rounded px-3 py-2 ${errors.voice_name ? "border-red-500" : ""}`}
          >
            <option value="">请选择语音</option>
            {voices.map(v => (
              <option key={v.voice_name} value={v.voice_name}>
                {v.voice_name} ({v.voice_type})
              </option>
            ))}
          </select>
          {errors.voice_name && <p className="text-red-500 text-sm mt-1">{errors.voice_name}</p>}
        </div>

          <div>
            <label className="block mb-1 font-medium">语速</label>
            <input
              name="speed_ratio"
              type="number"
              step="0.01"
              value={form.speed_ratio}
              onChange={handleChange}
              className="w-full border rounded px-3 py-2"
              min={0.5}
              max={3.0}
            />
          </div>

          {form.voice_name && (
            <div className="md:col-span-2 mt-2">
              <p className="text-sm text-gray-500 mb-1">试听：</p>
              <audio
                controls
                src={voices.find(v => v.voice_name === form.voice_name)?.url}
                className="w-full"
              />
            </div>
          )}
        </div>
      </div>


{/* 系统配置卡 */}
<div className="bg-white shadow-md rounded-lg p-6 space-y-4">
  <h3 className="text-xl font-medium border-b pb-2 mb-4">系统配置</h3>
  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
    {/* 系统类型选择 */}
    <div>
      <label className="block mb-1 font-medium">系统类型</label>
      <select
        name="system_type"
        value={form.system_type}
        onChange={handleChange}
        className="w-full border rounded px-3 py-2"
      >
        <option value="">请选择系统类型</option>
        <option value="Windows7">Windows7</option>
        <option value="Windows10">Windows10</option>
        <option value="Linux">Linux</option>
        <option value="macOS">macOS</option>
        <option value="Android">Android</option>
        <option value="iOS">iOS</option>
      </select>
    </div>

        {/* 基础文件路径 */}
        {/* 基础文件路径 */}
    <div>
      <label className="block mb-1 font-medium">基础文件路径</label>
      <div className="flex items-center space-x-2">
        <input
          type="text"
          name="base_file_path"
          value={form.base_file_path}
          onChange={handleChange}
          placeholder="例如：/data/assistants 或 C:\\projects\\ai-assistant"
          className="w-full border rounded px-3 py-2"
        />
      </div>
      <p className="text-sm text-gray-500 mt-1">
        请输入系统中的文件目录路径（例如服务器路径或挂载路径）
      </p>
    </div>
      </div>
    </div>

      <button
        type="submit"
        onClick={handleSubmit}
        className="w-full py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition text-lg font-medium"
      >
        保存
      </button>
    </div>
  );
}
