"""
AI Yordamchi xizmati — o'quvchi va talabalar uchun ingliz tili va boshqa fanlardan
uy vazifalarini qadamma-qadam, qoidalar asosida va o'zbek tilida yechib beruvchi intellektual modul.
Qo'llab-quvvatlanadi:
- Google Gemini 3.8 Flash (Matn va Rasm / Multimodal Vision)
- Pollinations AI (OpenAI GPT-4o arxitekturasi)
- Groq Cloud (Llama 3.3 70B Versatile)
- OpenAI (GPT-4o / GPT-4o-mini)
- Mahalliy Aqlli Dvigatel (Offline Local English & Math Solver)
"""

import re
import asyncio
import logging
from typing import Optional
from openai import AsyncOpenAI

from config import OPENAI_API_KEY, GROQ_API_KEY, GEMINI_API_KEY, POLLINATIONS_API_KEY
from services.english_service import english_service

logger = logging.getLogger(__name__)

ENGLISH_SYSTEM_PROMPT = (
    "Siz O'zbekistondagi maktab, litsey, kollej va universitet o'quvchilari uchun "
    "eng malakali, mehribon va professional Ingliz tili ustozi (AI English Tutor)siz.\n\n"
    "Vazifangiz: Ingliz tili bo'yicha berilgan har qanday topshiriqni (grammatika mashqlari, qavslarni ochish, "
    "test savollari, tarjima, insho, matn tahlili yoki rasm orqali berilgan sahifadagi topshiriqlarni) "
    "o'quvchi to'liq tushunadigan qilib, O'ZBEK TILIDA qadamma-qadam yechib berish.\n\n"
    "Javob berish andozasi:\n"
    "📌 **Vazifa / Savol:** (topshiriqning qisqacha mohiyati)\n"
    "💡 **Grammatika qoidasi (Rule):** (qaysi zamon, qoida, formula yoki predlog ishlatilayotgani, o'zbekcha qoidasi)\n"
    "📝 **Qadamma-qadam yechim:** (har bir gap, variant yoki bosqich tushuntirilgan holda)\n"
    "✅ **To'g'ri javob:** (aniq va ko'zga tashlanadigan qilib ko'rsating)\n"
    "💡 **Foydali maslahat (Pro Tip):** (bu qoidani test va imtihonda oson eslab qolish siri)\n\n"
    "Belgilarni chiroyli, o'qilishi oson Markdown formatida taqdim eting."
)

GENERAL_SYSTEM_PROMPT = (
    "Siz barcha maktab va oliygoh fanlari bo'yicha kuchli, tajribali AI Uy Vazifasi yordamchisisiz. "
    "Har bir topshiriqni o'zbek tilida bosqichma-bosqich, formulalar va qoidalarni ko'rsatgan holda "
    "tushunarli qilib yechib berasiz."
)


class AIService:
    def __init__(self):
        self._openai_client: Optional[AsyncOpenAI] = None
        self._groq_client: Optional[AsyncOpenAI] = None
        self._pollinations_client: Optional[AsyncOpenAI] = None
        self._gemini_client = None

        self._init_clients()

    def _init_clients(self):
        """Mavjud API kalitlari bo'yicha mijozlarni ishga tushirish."""
        # Pollinations mijozi
        pol_key = POLLINATIONS_API_KEY or GEMINI_API_KEY or "dummy_key"
        try:
            self._pollinations_client = AsyncOpenAI(
                api_key=pol_key,
                base_url="https://text.pollinations.ai/openai"
            )
            logger.info("Pollinations AI mijozi muvaffaqiyatli ulandi.")
        except Exception as e:
            logger.warning(f"Pollinations mijozini ulashda xatolik: {e}")

        # Google Gemini mijozi
        if GEMINI_API_KEY:
            try:
                from google import genai
                self._gemini_client = genai.Client(api_key=GEMINI_API_KEY)
                logger.info("Google Gemini mijozi muvaffaqiyatli ulandi.")
            except Exception as e:
                logger.warning(f"Google Gemini mijozini ulashda xatolik: {e}")

        # Groq mijozi
        if GROQ_API_KEY:
            try:
                self._groq_client = AsyncOpenAI(
                    api_key=GROQ_API_KEY,
                    base_url="https://api.groq.com/openai/v1"
                )
                logger.info("Groq AI mijozi muvaffaqiyatli ulandi.")
            except Exception as e:
                logger.warning(f"Groq mijozini ulashda xatolik: {e}")

        # OpenAI mijozi
        if OPENAI_API_KEY:
            try:
                self._openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
                logger.info("OpenAI mijozi muvaffaqiyatli ulandi.")
            except Exception as e:
                logger.warning(f"OpenAI mijozini ulashda xatolik: {e}")

    def update_keys(self, gemini_key: str = "", groq_key: str = "", openai_key: str = "", pollinations_key: str = ""):
        """Yangi kalitlarni dinamik o'rnatish."""
        global GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY, POLLINATIONS_API_KEY
        if gemini_key:
            GEMINI_API_KEY = gemini_key
        if groq_key:
            GROQ_API_KEY = groq_key
        if openai_key:
            OPENAI_API_KEY = openai_key
        if pollinations_key:
            POLLINATIONS_API_KEY = pollinations_key
        self._init_clients()

    def is_ai_available(self) -> bool:
        """Tashqi AI API mijozlaridan kamida bittasi ulanganmi?"""
        return bool(self._gemini_client or self._pollinations_client or self._groq_client or self._openai_client)

    async def solve_homework(
        self,
        question: str,
        subject: str = "🇬🇧 Ingliz tili",
        mode: str = "standard"
    ) -> str:
        """Vazifani AI orqali yechish."""
        is_english = "ingliz" in subject.lower() or "english" in subject.lower()
        sys_prompt = ENGLISH_SYSTEM_PROMPT if is_english else GENERAL_SYSTEM_PROMPT

        if mode == "simple":
            sys_prompt += "\n\nMUHIM: Buni eng oddiy, boshlang'ich sinf bolasi ham tushunadigan tilda tushuntirib bering."
        elif mode == "summary":
            sys_prompt += "\n\nMUHIM: Faqat qisqa xulosa, to'g'ri javob va asosiy qoidani bering. Ortiqcha gaplarsiz."

        user_content = f"Fan: {subject}\n\nTopshiriq:\n{question}"

        # 1. Google Gemini (gemini-3.8-flash)
        if self._gemini_client:
            try:
                prompt_full = f"{sys_prompt}\n\n{user_content}"
                res = await asyncio.wait_for(
                    self._gemini_client.aio.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=prompt_full
                    ),
                    timeout=5.0
                )
                if res and res.text:
                    return self._clean_response(res.text.strip())
            except Exception as e:
                logger.warning(f"Gemini API urinishi: {e}")

        # 2. Pollinations AI (OpenAI GPT-4o formati orqali)
        if self._pollinations_client:
            try:
                res = await self._pollinations_client.chat.completions.create(
                    model="openai",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.5,
                    timeout=25.0
                )
                if res.choices and res.choices[0].message.content:
                    return self._clean_response(res.choices[0].message.content.strip())
            except Exception as e:
                logger.warning(f"Pollinations API urinishi: {e}")

        # 3. Groq Cloud
        if self._groq_client:
            try:
                res = await self._groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.4,
                    timeout=25.0
                )
                if res.choices and res.choices[0].message.content:
                    return self._clean_response(res.choices[0].message.content.strip())
            except Exception as e:
                logger.warning(f"Groq API urinishi: {e}")

        # 4. OpenAI
        if self._openai_client:
            try:
                res = await self._openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": user_content}
                    ],
                    temperature=0.4,
                    timeout=25.0
                )
                if res.choices and res.choices[0].message.content:
                    return self._clean_response(res.choices[0].message.content.strip())
            except Exception as e:
                logger.warning(f"OpenAI API urinishi: {e}")

        # 5. Mahalliy Ingliz Tili va Matematika Eksperti (Offline Fallback)
        local_solution = self._solve_locally(question, subject)
        if local_solution:
            return local_solution

        return (
            "🇬🇧 **Ingliz tili uy vazifasi qabul qilindi!**\n\n"
            "Serverda vaqtincha yuklama yuqori bo'lganligi sababli, savolingizni "
            "yana bir bor yuborishingizni yoki aniqroq qilib yozishingizni so'raymiz."
        )

    async def solve_photo(self, image_bytes: bytes, mime_type: str = "image/jpeg", caption: str = "") -> str:
        """Rasm orqali berilgan uy vazifasini yechish (Multimodal Vision)."""
        prompt = (
            "Siz professional Ingliz tili ustozi va vazifa yechuvchisisiz. "
            "Ushbu rasmda berilgan daftardagi yoki kitobdagi barcha ingliz tili mashqlarini, "
            "savollarini yoki testlarini aniqlang va har birini o'zbek tilida qadamma-qadam, "
            "1, 2, 3... tartib raqamlari bilan to'liq va to'g'ri yechib bering."
        )
        if caption:
            prompt += f"\nFoydalanuvchi izohi: {caption}"

        if self._gemini_client:
            try:
                from google.genai import types
                image_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
                res = await self._gemini_client.aio.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=[prompt, image_part]
                )
                if res and res.text:
                    return self._clean_response(res.text.strip())
            except Exception as e:
                logger.error(f"Gemini Vision xatosi: {e}")

        return (
            "📷 **Rasm qabul qilindi!**\n\n"
            "💡 Rasmdagi topshiriqlarni sun'iy intellekt orqali avtomatik yechish uchun "
            "rasm aniq va yorug' tushgan bo'lishi kerak.\n\n"
            "Agar rasm noaniq bo'lsa, mashq matnini to'g'ridan-to'g'ri yozib yuboring — bot soniyalar ichida yechib beradi!"
        )

    async def check_essay(self, text: str) -> str:
        """O'quvchi yozgan insho (essay) yoki matnni tekshirish va xatolarini tuzatish."""
        prompt = (
            "Siz tajribali ingliz tili o'qituvchisiz (IELTS Examiner). "
            "Quyidagi o'quvchi tomonidan yozilgan inglizcha matn / inshoni tekshiring:\n\n"
            f"Matn:\n«{text}»\n\n"
            "Tahlilni quyidagi tartibda bering:\n"
            "1. 📊 **Umumiy baho va daraja** (A2, B1, B2 yoki IELTS taxminiy ball)\n"
            "2. ❌ **Topilgan xatolar va tuzatishlar:** (qaysi so'z xato yozilgan va qoidasi nima)\n"
            "3. ✨ **Tuzatilgan mukammal variant:** (matnning to'g'irlangan to'liq ko'rinishi)\n"
            "4. 💡 **Yaxshilash uchun tavsiyalar:**"
        )
        return await self.solve_homework(prompt, subject="🇬🇧 Ingliz tili")

    def _solve_locally(self, question: str, subject: str) -> Optional[str]:
        """Internet yoki API bo'lmaganda mahalliy tahlil qilish."""
        q = question.strip()

        # 1. Ingliz tili: Noto'g'ri fe'llar qidiruvi
        verbs = english_service.search_irregular_verb(q)
        if verbs:
            v = verbs[0]
            return (
                f"📚 **Noto'g'ri fe'l (Irregular Verb) topildi:**\n\n"
                f"🔹 **V1 (Infinitive):** `{v['v1']}`\n"
                f"🔹 **V2 (Past Simple):** `{v['v2']}`\n"
                f"🔹 **V3 (Past Participle):** `{v['v3']}`\n"
                f"🇺🇿 **O'zbekcha ma'nosi:** **{v['uz']}**\n\n"
                f"📝 **Namunaviy gap:**\n"
                f"> *{v['ex']}*"
            )

        # 2. Ingliz tili: Qavslarni ochish mashqi
        bracket_sol = english_service.solve_open_brackets(q)
        if bracket_sol:
            return bracket_sol

        # 3. Oddiy matematika / algebra (agar matematika savoli kelsa)
        eq_match = re.search(r'([+-]?\s*\d*)\s*([a-zA-Z])\s*([+-]\s*\d+)\s*=\s*([+-]?\s*\d+)', q.lower())
        if eq_match:
            try:
                a_str = eq_match.group(1).replace(" ", "")
                var_name = eq_match.group(2)
                b_str = eq_match.group(3).replace(" ", "")
                c_str = eq_match.group(4).replace(" ", "")

                a = int(a_str) if a_str and a_str not in ["+", "-"] else (-1 if a_str == "-" else 1)
                b = int(b_str)
                c = int(c_str)

                rhs = c - b
                x = rhs / a
                x_val = int(x) if x.is_integer() else round(x, 2)
                sign_str = f"+ {abs(b)}" if b >= 0 else f"- {abs(b)}"

                return (
                    f"📌 **Tenglama:** `{a}{var_name} {sign_str} = {c}`\n\n"
                    f"📝 **Qadamma-qadam yechim:**\n"
                    f"1. `{a}{var_name} = {c} - ({b})` => `{a}{var_name} = {rhs}`\n"
                    f"2. `{var_name} = {rhs} ÷ {a}` => `{var_name} = {x_val}`\n\n"
                    f"✅ **Yakuniy javob:** `{var_name} = {x_val}`"
                )
            except Exception:
                pass

        # Oddiy arifmetika: 25 * 4 + 10
        clean_math = re.sub(r'[^0-9\+\-\*\/\(\)\.\s]', '', q)
        if clean_math and any(op in clean_math for op in ['+', '-', '*', '/']) and len(clean_math) >= 3:
            try:
                allowed_chars = set("0123456789+-*/(). ")
                if set(clean_math).issubset(allowed_chars):
                    res = eval(clean_math, {"__builtins__": None}, {})
                    res_val = int(res) if isinstance(res, float) and res.is_integer() else round(res, 4)
                    return f"📌 **Ifoda:** `{clean_math.strip()}`\n\n✅ **Natija:** `{res_val}`"
            except Exception:
                pass

        return None

    def _clean_response(self, text: str) -> str:
        """Javobdagi belgilar va latexni tartibga keltirish hamda reklamalarni tozalash."""
        text = re.sub(r'\\\[(.*?)\\\]', r'\n\1\n', text, flags=re.DOTALL)
        text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
        # Reklama va tashqi havolalarni tozalash
        text = re.sub(r'---\s*\n\s*\*\*Support Pollinations.*?$', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'🌸\s*\*\*Ad\*\*.*?$', '', text, flags=re.DOTALL | re.IGNORECASE)
        return text.strip()


ai_service = AIService()
