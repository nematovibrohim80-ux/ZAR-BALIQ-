import asyncio
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from config import BOT_TOKEN, GROQ_API_KEY
from aiogram import Bot
from openai import AsyncOpenAI

async def test_all():
    print("1. Telegram Bot Token tekshirilmoqda...")
    bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"   -> Muvaffaqiyatli! Bot: @{me.username} ({me.first_name}), ID: {me.id}")
    await bot.session.close()

    print("\n2. Groq AI tekshirilmoqda...")
    client = AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=GROQ_API_KEY
    )
    prompt = "Salom, bugun juda charchadim."
    res = await client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {"role": "system", "content": "Sening isming: Hamroh AI. Samimiy do'stona AI assistentsan."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )
    reply = res.choices[0].message.content.strip()
    print(f"   -> Groq javobi:\n{reply}")
    print("\nBARCHA TEKSHIRUVLAR 100% MUVAFFAQIYATLI!")

if __name__ == "__main__":
    asyncio.run(test_all())
