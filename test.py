import base64

from backend.app.core.settings import settings
from backend.app.utils.voice_util import text_to_speech_segments, merge_audio_base64_segments, TTSClient

stream_tokens = [
    "你好", "，", "今天天气", "不错", "，", "适合", "出门", "散步", "。",
    "要不要", "我", "帮你", "查查", "附近", "的", "公园", "？"
]

tts = TTSClient(settings.TTS_AND_ASR_API_KEY)





audio_segments, remain_text =  text_to_speech_segments(stream_tokens,tts.text_to_speech)

print("剩余未播文本：", remain_text)

# 2️⃣ 拼接为完整音频
final_audio_b64 = merge_audio_base64_segments(audio_segments)

# 3️⃣ （可选）保存为文件试听
with open("final_output.mp3", "wb") as f:
    f.write(base64.b64decode(final_audio_b64))

print("🎧 已生成完整音频文件：final_output.wav")