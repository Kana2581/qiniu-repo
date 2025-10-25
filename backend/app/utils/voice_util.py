"""
voice_util.py - 七牛云语音工具集（TTS + ASR）
----------------------------------------------
功能：
- 文本转语音 (Text-to-Speech)
- 语音转文本 (Automatic Speech Recognition)

示例：
    from voice_util import TTSClient, ASRClient

    tts = TTSClient(api_key="your_api_key_here")
    tts.text_to_speech("你好，世界", "hello.mp3")

    asr = ASRClient(api_key="your_api_key_here")
    result = asr.speech_to_text("https://example.com/audio.mp3")
    print(result)
"""

import requests
import base64


# =====================
# TTS 客户端
# =====================
import requests
import base64

class TTSClient:
    def __init__(self, api_key: str, base_url: str = "https://openai.qiniu.com/v1/voice/tts"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"{self.api_key}"
        }

    def text_to_speech(
        self,
        text: str,
        voice_type: str = "qiniu_zh_female_wwxkjx",
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
    ) -> str | None:
        """
        返回生成的语音二进制数据
        """
        payload = {
            "audio": {
                "voice_type": voice_type,
                "encoding": encoding,
                "speed_ratio": speed_ratio
            },
            "request": {
                "text": text
            }
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None

        data = response.json()
        audio_base64 = data.get("audio") or data.get("data")
        return audio_base64


    def base64_to_bytes(self,audio_base64)-> bytes|None:
        if not audio_base64:
            return None

        try:
            audio_bytes = base64.b64decode(audio_base64)
            return audio_bytes
        except Exception as e:
            print(f"解码音频数据失败：{e}")
            return None



# =====================
# ASR 客户端
# =====================
class ASRClient:
    def __init__(self, api_key: str, base_url: str = "https://openai.qiniu.com/v1/voice/asr"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def speech_to_text(self, audio_url: str, audio_format: str = "mp3"):
        """
        调用 ASR 接口进行语音识别
        :param audio_url: 音频文件的公网 URL
        :param audio_format: 音频格式（默认 mp3）
        :return: 识别出的文本或 None
        """
        payload = {
            "model": "asr",
            "audio": {
                "format": audio_format,
                "url": audio_url
            }
        }

        try:
            response = requests.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"请求出错: {e}")
            return None

        data = response.json()
        try:
            text = data["data"]["result"]["text"]
            print(f"✅ 识别结果: {text}")
            return text
        except KeyError:
            print("⚠️ 未找到识别文本，请检查响应结构：")
            print(data)
            return None
