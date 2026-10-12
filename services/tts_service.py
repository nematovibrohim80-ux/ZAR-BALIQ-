"""
Ovozli talaffuz (TTS — Text-to-Speech) xizmati.
Inglizcha so'z va gaplarni to'g'ri, toza britancha/amerika talaffuzida audio (MP3) formatda tayyorlaydi.
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

AUDIO_DIR = Path("assets/audio")
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


class TTSService:
    @staticmethod
    def extract_english_sentence(text: str) -> str:
        """Matndan asosiy inglizcha gap yoki so'zni ajratib olish."""
        # 1. Agar kod bloki yoki qo'shtirnoq ichidagi inglizcha bo'lsa
        quotes = re.findall(r'[`"«]([A-Za-z0-9\s\,\.\?\!\'\-]+)[`"»]', text)
        for q in quotes:
            if re.search(r'[A-Za-z]', q) and len(q.strip()) > 3:
                return q.strip()

        # 2. Inglizcha gaplarni topish
        lines = text.split("\n")
        for line in lines:
            cleaned = re.sub(r'[*_#`~]', '', line).strip()
            # Agar satr asosan inglizcha harflardan iborat bo'lsa
            english_chars = len(re.findall(r'[A-Za-z]', cleaned))
            if english_chars > 8 and "o'zbek" not in cleaned.lower() and "javob" not in cleaned.lower():
                return cleaned

        # 3. Aks holda qisqa qilib berish
        eng_words = re.findall(r'\b[A-Za-z]{2,}\b', text)
        if eng_words:
            return " ".join(eng_words[:12])
        return "Hello, practice your English pronunciation every day!"

    @classmethod
    def generate_audio(cls, text: str, filename_prefix: str = "pronounce") -> Optional[str]:
        """Inglizcha matnni MP3 faylga aylantirib, fayl yo'lini qaytarish."""
        try:
            target_text = cls.extract_english_sentence(text)
            if not target_text or len(target_text.strip()) < 2:
                target_text = text[:150]

            # 200 belgidan oshirmaslik (tez yuklanishi uchun)
            target_text = target_text[:200].strip()

            out_path = AUDIO_DIR / f"{filename_prefix}_{abs(hash(target_text)) % 1000000}.mp3"
            
            # Agar fayl allaqachon mavjud bo'lsa qaytaramiz
            if out_path.exists() and out_path.stat().st_size > 0:
                return str(out_path)

            tts = gTTS(text=target_text, lang="en", tld="com")
            tts.save(str(out_path))
            return str(out_path)
        except Exception as e:
            logger.error(f"TTS audio generatsiyasida xatolik: {e}")
            return None


tts_service = TTSService()
