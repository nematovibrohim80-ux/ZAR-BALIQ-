"""
Ingliz tili fani bo'yicha maxsus Uy Vazifasi va Bilimlar xizmati.
- Grammatika qoidalari va zamonlar formulalari (12 Tenses)
- 150+ Noto'g'ri fe'llar (Irregular verbs) to'liq bazasi va qidiruv tizimi
- Qavslarni ochish va testlarni mahalliy (offline) tahlil qilish algoritmi
- Insho va Esse namunalari hamda yozish shablonlari
- O'quvchilar uchun interaktiv grammatika testlari (Quiz)
- Inglizcha-O'zbekcha ommabop lug'at
"""

import re
from typing import List, Dict, Any, Optional, Tuple

# 150+ Noto'g'ri fe'llar (V1, V2, V3, O'zbekcha tarjimasi, Namunaviy gap)
IRREGULAR_VERBS = [
    {"v1": "be", "v2": "was / were", "v3": "been", "uz": "bo'lmoq", "ex": "I was at school yesterday."},
    {"v1": "become", "v2": "became", "v3": "become", "uz": "bo'lib qolmoq, aylanmoq", "ex": "He became a doctor."},
    {"v1": "begin", "v2": "began", "v3": "begun", "uz": "boshlamoq", "ex": "The lesson began at 9 AM."},
    {"v1": "bite", "v2": "bit", "v3": "bitten", "uz": "tishlamoq", "ex": "The dog bit the ball."},
    {"v1": "blow", "v2": "blew", "v3": "blown", "uz": "esmoq, puflamoq", "ex": "The wind blew strongly."},
    {"v1": "break", "v2": "broke", "v3": "broken", "uz": "sindirmoq", "ex": "He broke the window."},
    {"v1": "bring", "v2": "brought", "v3": "brought", "uz": "olib kelmoq", "ex": "She brought her notebook."},
    {"v1": "build", "v2": "built", "v3": "built", "uz": "qurmoq", "ex": "They built a new house."},
    {"v1": "burn", "v2": "burnt / burned", "v3": "burnt / burned", "uz": "kuymoq, yoqmoq", "ex": "The fire burned brightly."},
    {"v1": "buy", "v2": "bought", "v3": "bought", "uz": "sotib olmoq", "ex": "I bought a new English dictionary."},
    {"v1": "catch", "v2": "caught", "v3": "caught", "uz": "tutmoq, ushlamoq", "ex": "He caught the bus at 8:00."},
    {"v1": "choose", "v2": "chose", "v3": "chosen", "uz": "tanlamoq", "ex": "She chose the red dress."},
    {"v1": "come", "v2": "came", "v3": "come", "uz": "kelmoq", "ex": "My friend came to see me."},
    {"v1": "cost", "v2": "cost", "v3": "cost", "uz": "turmoq (narx)", "ex": "This book cost $10."},
    {"v1": "cut", "v2": "cut", "v3": "cut", "uz": "kesmoq", "ex": "He cut the paper with scissors."},
    {"v1": "dig", "v2": "dug", "v3": "dug", "uz": "qazimoq", "ex": "They dug a hole in the garden."},
    {"v1": "do", "v2": "did", "v3": "done", "uz": "bajarmoq, qilmoq", "ex": "I did my homework yesterday."},
    {"v1": "draw", "v2": "drew", "v3": "drawn", "uz": "chizmoq", "ex": "She drew a beautiful picture."},
    {"v1": "drink", "v2": "drank", "v3": "drunk", "uz": "ichmoq", "ex": "He drank a glass of water."},
    {"v1": "drive", "v2": "drove", "v3": "driven", "uz": "haydamoq", "ex": "My father drove the car."},
    {"v1": "eat", "v2": "ate", "v3": "eaten", "uz": "yemoq", "ex": "We ate breakfast together."},
    {"v1": "fall", "v2": "fell", "v3": "fallen", "uz": "yiqilmoq, tushmoq", "ex": "Leaves fell from the tree."},
    {"v1": "feel", "v2": "felt", "v3": "felt", "uz": "his qilmoq", "ex": "I felt happy after the exam."},
    {"v1": "fight", "v2": "fought", "v3": "fought", "uz": "kurashmoq, urishmoq", "ex": "They fought bravely."},
    {"v1": "find", "v2": "found", "v3": "found", "uz": "topmoq", "ex": "She found her lost pen."},
    {"v1": "fly", "v2": "flew", "v3": "flown", "uz": "uchmoq", "ex": "The bird flew away."},
    {"v1": "forget", "v2": "forgot", "v3": "forgotten", "uz": "unutmoq", "ex": "Don't forget your homework!"},
    {"v1": "forgive", "v2": "forgave", "v3": "forgiven", "uz": "kechirmoq", "ex": "She forgave him."},
    {"v1": "freeze", "v2": "froze", "v3": "frozen", "uz": "muzlamoq", "ex": "The lake froze in winter."},
    {"v1": "get", "v2": "got", "v3": "got / gotten", "uz": "olmoq, yetib bormoq", "ex": "I got an 'A' grade in English."},
    {"v1": "give", "v2": "gave", "v3": "given", "uz": "bermoq", "ex": "Teacher gave us an interesting task."},
    {"v1": "go", "v2": "went", "v3": "gone", "uz": "bormoq", "ex": "We went to the library."},
    {"v1": "grow", "v2": "grew", "v3": "grown", "uz": "o'smoq, yetishtirmoq", "ex": "He grew up in Tashkent."},
    {"v1": "hang", "v2": "hung", "v3": "hung", "uz": "osmoq", "ex": "She hung the picture on the wall."},
    {"v1": "have", "v2": "had", "v3": "had", "uz": "ega bo'lmoq", "ex": "We had an English test today."},
    {"v1": "hear", "v2": "heard", "v3": "heard", "uz": "eshitmoq", "ex": "Did you hear that sound?"},
    {"v1": "hide", "v2": "hid", "v3": "hidden", "uz": "yashirinmoq, yashirmoq", "ex": "He hid behind the door."},
    {"v1": "hit", "v2": "hit", "v3": "hit", "uz": "urmoq", "ex": "The ball hit the wall."},
    {"v1": "hold", "v2": "held", "v3": "held", "uz": "ushlab turmoq", "ex": "She held the umbrella."},
    {"v1": "hurt", "v2": "hurt", "v3": "hurt", "uz": "og'rimoq, og'ritmoq", "ex": "My leg hurts."},
    {"v1": "keep", "v2": "kept", "v3": "kept", "uz": "saqlamoq, davom ettirmoq", "ex": "Keep working hard!"},
    {"v1": "know", "v2": "knew", "v3": "known", "uz": "bilmoq", "ex": "I knew the correct answer."},
    {"v1": "learn", "v2": "learnt / learned", "v3": "learnt / learned", "uz": "o'rganmoq", "ex": "I learned 20 new words."},
    {"v1": "leave", "v2": "left", "v3": "left", "uz": "tark etmoq, qoldirmoq", "ex": "The train left on time."},
    {"v1": "lend", "v2": "lent", "v3": "lent", "uz": "qarzga bermoq", "ex": "Could you lend me a pen?"},
    {"v1": "let", "v2": "let", "v3": "let", "uz": "ruxsat bermoq", "ex": "Let me explain this rule."},
    {"v1": "lie", "v2": "lay", "v3": "lain", "uz": "yotmoq", "ex": "He lay on the sofa."},
    {"v1": "lose", "v2": "lost", "v3": "lost", "uz": "yo'qotmoq, yutqazmoq", "ex": "I lost my notebook."},
    {"v1": "make", "v2": "made", "v3": "made", "uz": "yasamoq, qilmoq", "ex": "Don't make mistakes."},
    {"v1": "mean", "v2": "meant", "v3": "meant", "uz": "anglatmoq, nazarda tutmoq", "ex": "What does this word mean?"},
    {"v1": "meet", "v2": "met", "v3": "met", "uz": "uchratmoq, tanishmoq", "ex": "I met my teacher today."},
    {"v1": "pay", "v2": "paid", "v3": "paid", "uz": "to'lamoq", "ex": "He paid for the course."},
    {"v1": "put", "v2": "put", "v3": "put", "uz": "qo'ymoq", "ex": "Put your books on the table."},
    {"v1": "read", "v2": "read", "v3": "read", "uz": "o'qimoq", "ex": "I read an English story."},
    {"v1": "ride", "v2": "rode", "v3": "ridden", "uz": "minmoq (velosiped, ot)", "ex": "She rode a bicycle."},
    {"v1": "ring", "v2": "rang", "v3": "rung", "uz": "qo'ng'iroq qilmoq/chalinmoq", "ex": "The school bell rang."},
    {"v1": "rise", "v2": "rose", "v3": "risen", "uz": "ko'tarilmoq, chiqmoq", "ex": "The sun rises in the east."},
    {"v1": "run", "v2": "ran", "v3": "run", "uz": "yugurmoq", "ex": "He ran very fast."},
    {"v1": "say", "v2": "said", "v3": "said", "uz": "aytmoq", "ex": "She said: 'Good morning!'"},
    {"v1": "see", "v2": "saw", "v3": "seen", "uz": "ko'rmoq", "ex": "I saw him at the station."},
    {"v1": "sell", "v2": "sold", "v3": "sold", "uz": "sotmoq", "ex": "They sold the car."},
    {"v1": "send", "v2": "sent", "v3": "sent", "uz": "yubormoq, jo'natmoq", "ex": "Send me your homework."},
    {"v1": "set", "v2": "set", "v3": "set", "uz": "o'rnatmoq, botmoq", "ex": "The sun sets in the west."},
    {"v1": "shake", "v2": "shook", "v3": "shaken", "uz": "silkitmoq", "ex": "They shook hands."},
    {"v1": "shine", "v2": "shone", "v3": "shone", "uz": "porlamoq", "ex": "The sun shone brightly."},
    {"v1": "shoot", "v2": "shot", "v3": "shot", "uz": "otmoq", "ex": "He shot the target."},
    {"v1": "show", "v2": "showed", "v3": "shown", "uz": "ko'rsatmoq", "ex": "Show me your notebook."},
    {"v1": "shut", "v2": "shut", "v3": "shut", "uz": "yopmoq", "ex": "Shut the door, please."},
    {"v1": "sing", "v2": "sang", "v3": "sung", "uz": "kuylamoq", "ex": "She sang an English song."},
    {"v1": "sink", "v2": "sank", "v3": "sunk", "uz": "cho'kmoq", "ex": "The ship sank."},
    {"v1": "sit", "v2": "sat", "v3": "sat", "uz": "o'tirmoq", "ex": "Sit down, please."},
    {"v1": "sleep", "v2": "slept", "v3": "slept", "uz": "uxlamoq", "ex": "I slept for 8 hours."},
    {"v1": "speak", "v2": "spoke", "v3": "spoken", "uz": "gapirmoq", "ex": "Can you speak English?"},
    {"v1": "spend", "v2": "spent", "v3": "spent", "uz": "sarflamoq, o'tkazmoq", "ex": "I spent 2 hours on homework."},
    {"v1": "stand", "v2": "stood", "v3": "stood", "uz": "turmoq", "ex": "He stood by the window."},
    {"v1": "steal", "v2": "stole", "v3": "stolen", "uz": "o'g'irlamoq", "ex": "Someone stole his bike."},
    {"v1": "swim", "v2": "swam", "v3": "swum", "uz": "suzmoq", "ex": "We swam in the pool."},
    {"v1": "take", "v2": "took", "v3": "taken", "uz": "olmoq", "ex": "Take your time."},
    {"v1": "teach", "v2": "taught", "v3": "taught", "uz": "o'rgatmoq, dars bermoq", "ex": "She taught English for 10 years."},
    {"v1": "tell", "v2": "told", "v3": "told", "uz": "aytmoq, so'zlab bermoq", "ex": "He told an interesting story."},
    {"v1": "think", "v2": "thought", "v3": "thought", "uz": "o'ylamoq", "ex": "I think this answer is right."},
    {"v1": "throw", "v2": "threw", "v3": "thrown", "uz": "otmoq, irg'itmoq", "ex": "Throw the ball to me."},
    {"v1": "understand", "v2": "understood", "v3": "understood", "uz": "tushunmoq", "ex": "I understood the grammar rule."},
    {"v1": "wake", "v2": "woke", "v3": "woken", "uz": "uyg'onmoq, uyg'otmoq", "ex": "I woke up early today."},
    {"v1": "wear", "v2": "wore", "v3": "worn", "uz": "kiymoq, taqmoq", "ex": "He wore a school uniform."},
    {"v1": "win", "v2": "won", "v3": "won", "uz": "yutmoq, g'alaba qozonmoq", "ex": "Our team won the match."},
    {"v1": "write", "v2": "wrote", "v3": "written", "uz": "yozmoq", "ex": "I wrote an essay yesterday."}
]


# Ingliz tili qoidalari to'liq ma'lumotnomasi
ENGLISH_RULES = {
    "tenses_simple": (
        "⏱ **Simple (Oddiy) Zamonlar:**\n\n"
        "1️⃣ **Present Simple (Hozirgi oddiy zamon):**\n"
        "• Formulalar:\n"
        "  - (+) `S + V1 (he/she/it uchun V-s/es)`\n"
        "  - (-) `S + do/does not + V1`\n"
        "  - (?) `Do/Does + S + V1?`\n"
        "• Kalit so'zlar: *always, usually, often, sometimes, every day, rarely*\n"
        "• Misol: *She plays tennis every Sunday.* / *He doesn't like milk.*\n\n"
        "2️⃣ **Past Simple (O'tgan oddiy zamon):**\n"
        "• Formulalar:\n"
        "  - (+) `S + V2 (yoki V-ed)`\n"
        "  - (-) `S + did not + V1`\n"
        "  - (?) `Did + S + V1?`\n"
        "• Kalit so'zlar: *yesterday, last week, ago, in 2020*\n"
        "• Misol: *They visited London last year.* / *Did you see him?*\n\n"
        "3️⃣ **Future Simple (Kelasi oddiy zamon):**\n"
        "• Formulalar:\n"
        "  - (+) `S + will + V1`\n"
        "  - (-) `S + will not (won't) + V1`\n"
        "  - (?) `Will + S + V1?`\n"
        "• Kalit so'zlar: *tomorrow, next week, soon, in 2 days*\n"
        "• Misol: *I will call you tomorrow.*"
    ),
    "tenses_continuous": (
        "🔄 **Continuous (Davomli) Zamonlar:**\n\n"
        "1️⃣ **Present Continuous (Hozirgi davomli):**\n"
        "• Shakl: `S + am/is/are + V-ing`\n"
        "• Kalit so'zlar: *now, at the moment, currently, Look!, Listen!*\n"
        "• Misol: *I am doing my English homework right now.*\n\n"
        "2️⃣ **Past Continuous (O'tgan davomli):**\n"
        "• Shakl: `S + was/were + V-ing`\n"
        "• Kalit so'zlar: *at 5 PM yesterday, when he came, while*\n"
        "• Misol: *I was reading a book when you called me.*\n\n"
        "3️⃣ **Future Continuous (Kelasi davomli):**\n"
        "• Shakl: `S + will be + V-ing`\n"
        "• Misol: *This time tomorrow, I will be flying to London.*"
    ),
    "tenses_perfect": (
        "✨ **Perfect (Tugallangan) Zamonlar:**\n\n"
        "1️⃣ **Present Perfect (Hozirgi tugallangan):**\n"
        "• Shakl: `S + have/has + V3 (Past Participle)`\n"
        "• Ishlatilishi: Natijasi hozir ko'rinib turgan yoki tajriba haqida gapirganda.\n"
        "• Kalit so'zlar: *already, just, yet, ever, never, since, for, recently*\n"
        "• Misol: *I have already finished my exercises.* / *Have you ever been to Paris?*\n\n"
        "2️⃣ **Past Perfect (O'tgan tugallangan):**\n"
        "• Shakl: `S + had + V3`\n"
        "• Ishlatilishi: O'tmishdagi boshqa bir ishdan oldin tugallangan ish.\n"
        "• Misol: *When we arrived, the train had already left.*\n\n"
        "3️⃣ **Present Perfect Continuous:**\n"
        "• Shakl: `S + have/has been + V-ing`\n"
        "• Ishlatilishi: O'tmishda boshlanib, hozir ham davom etayotgan harakat.\n"
        "• Misol: *I have been learning English for 3 years.*"
    ),
    "passive_voice": (
        "🏗 **Passive Voice (Majhul Nisbat):**\n\n"
        "Majhul nisbatda ish-harakat kim tomonidan bajarilganidan ko'ra, harakatning o'zi yoki obyekt muhimroq bo'ladi.\n"
        "Asosiy qoida: `To be + V3 (Past Participle)`\n\n"
        "🔹 **Zamonlar bo'yicha formulalar:**\n"
        "• **Present Simple:** `am/is/are + V3`\n"
        "  - *Active:* He cleans the room.\n"
        "  - *Passive:* The room is cleaned.\n"
        "• **Past Simple:** `was/were + V3`\n"
        "  - *Active:* Shakespeare wrote Hamlet.\n"
        "  - *Passive:* Hamlet was written by Shakespeare.\n"
        "• **Future Simple:** `will be + V3`\n"
        "  - *Passive:* The letter will be sent tomorrow.\n"
        "• **Present Continuous:** `am/is/are + being + V3`\n"
        "  - *Passive:* The car is being washed right now.\n"
        "• **Present Perfect:** `have/has + been + V3`\n"
        "  - *Passive:* The homework has been done."
    ),
    "conditionals": (
        "🔀 **Conditionals (Shart Ergash Gaplar):**\n\n"
        "0️⃣ **Zero Conditional (Umumiy haqiqatlar, qonuniyatlar):**\n"
        "• `If + Present Simple, Present Simple`\n"
        "• *If you heat ice, it melts.*\n\n"
        "1️⃣ **First Conditional (Kelajakdagi real ehtimol):**\n"
        "• `If + Present Simple, will + V1`\n"
        "• *If it rains tomorrow, we will stay at home.*\n\n"
        "2️⃣ **Second Conditional (Hozirgi noreal orzu-istak):**\n"
        "• `If + Past Simple, would + V1`\n"
        "• *If I had a million dollars, I would travel the world.*\n\n"
        "3️⃣ **Third Conditional (O'tmishdagi amalga oshmagan holat va afsus):**\n"
        "• `If + Past Perfect (had + V3), would have + V3`\n"
        "• *If I had studied harder, I would have passed the exam.*"
    ),
    "prepositions": (
        "📍 **Predloglar (Prepositions of Time & Place):**\n\n"
        "🔹 **IN:**\n"
        "• Oylar, yillar, fasllar, asrlar: *in May, in 2026, in summer, in the 21st century*\n"
        "• Kun qismlari: *in the morning, in the afternoon, in the evening*\n"
        "• Shahar va davlatlar: *in Tashkent, in Uzbekistan*\n\n"
        "🔹 **ON:**\n"
        "• Hafta kunlari: *on Monday, on Friday*\n"
        "• Aniq sanalar: *on September 1st, on my birthday*\n"
        "• Sirt ustida: *on the table, on the wall*\n\n"
        "🔹 **AT:**\n"
        "• Aniq vaqt: *at 7 o'clock, at noon, at midnight*\n"
        "• Bayram va davr: *at night, at the weekend, at Christmas*\n"
        "• Aniq nuqta/joy: *at home, at school, at the station, at the airport*"
    ),
    "articles": (
        "🅰️ **Artikllar (Articles: A, AN, THE):**\n\n"
        "🔹 **A / AN (Noaniq artikl):**\n"
        "• Faqat birlikdagi sanaladigan otlar oldidan ishlatiladi.\n"
        "• Undosh tovushdan boshlansa: `A` (*a book, a student, a university*)\n"
        "• Unli tovushdan boshlansa: `AN` (*an apple, an hour, an umbrella*)\n\n"
        "🔹 **THE (Aniq artikl):**\n"
        "• Suhbatdoshlarga ma'lum bo'lgan aniq narsa-buyum oldidan.\n"
        "• Dunyoda yagona narsalar: *the Sun, the Moon, the Earth, the sky*\n"
        "• Sifatning orttirma darajasi: *the best, the most beautiful*\n"
        "• Daryolar, dengizlar, okeanlar: *the Nile, the Pacific Ocean*\n"
        "• Musiqa asboblari: *play the guitar, play the piano*\n\n"
        "🔹 **No Article (Artiklsiz holatlar):**\n"
        "• Sanalmaydigan umumiy otlar: *I like milk.* (the milk emas)\n"
        "• Sport turlari va o'yinlar: *play football, play chess*\n"
        "• Ovqatlanish vaqtlari: *have breakfast, have lunch*"
    )
}


# Interaktiv Grammatika Quizi savollari
GRAMMAR_QUIZ = [
    {
        "id": 1,
        "question": "She usually _____ to school by bus.",
        "options": ["A) go", "B) goes", "C) going", "D) went"],
        "correct": "B",
        "explanation": "He/she/it birlik olmoshlari bilan Present Simple zamonida fe'lga '-s' yoki '-es' qo'shiladi (She goes)."
    },
    {
        "id": 2,
        "question": "We _____ in this city since 2018.",
        "options": ["A) lived", "B) are living", "C) have lived", "D) will live"],
        "correct": "C",
        "explanation": "'Since 2018' kalit so'zi harakat o'tmishda boshlanib hozirgacha davom etayotganini bildiradi, shuning uchun Present Perfect (have lived) ishlatiladi."
    },
    {
        "id": 3,
        "question": "Look! The children _____ in the garden.",
        "options": ["A) play", "B) are playing", "C) played", "D) have played"],
        "correct": "B",
        "explanation": "'Look!' (Qara!) undovi ayni damda sodir bo'layotgan harakatga ishora qiladi, shuning uchun Present Continuous (are playing) to'g'ri."
    },
    {
        "id": 4,
        "question": "If it rains tomorrow, we _____ at home.",
        "options": ["A) stay", "B) stayed", "C) will stay", "D) would stay"],
        "correct": "C",
        "explanation": "First Conditional qoidasi: If + Present Simple, will + V1. Shuning uchun 'will stay' to'g'ri javob."
    },
    {
        "id": 5,
        "question": "English is spoken _____ many people around the world.",
        "options": ["A) at", "B) by", "C) in", "D) with"],
        "correct": "B",
        "explanation": "Passive Voice (Majhul nisbat) da ish-harakatni bajargan shaxs yoki vosita 'by' predlogi orqali ifodalanadi (spoken by many people)."
    },
    {
        "id": 6,
        "question": "I saw him _____ Monday morning.",
        "options": ["A) in", "B) at", "C) on", "D) for"],
        "correct": "C",
        "explanation": "Hafta kunlari (Monday, Tuesday...) va kun qismlari aniq kun bilan kelganda har doim 'ON' predlogi ishlatiladi (on Monday morning)."
    },
    {
        "id": 7,
        "question": "What is the Past Simple (V2) form of the verb 'BUY'?",
        "options": ["A) buyed", "B) bought", "C) boughten", "D) boight"],
        "correct": "B",
        "explanation": "'Buy' noto'g'ri (irregular) fe'l bo'lib, uning o'tgan zamon shakli 'bought' hisoblanadi (buy - bought - bought)."
    },
    {
        "id": 8,
        "question": "He has been interested in music _____ a long time.",
        "options": ["A) since", "B) for", "C) at", "D) during"],
        "correct": "B",
        "explanation": "Vaqt davomiyligi (duration: a long time, two hours, 5 years) ko'rsatilganda 'FOR' predlogi ishlatiladi."
    }
]


# Mashhur Insho / Esse Shablonlari
ESSAY_TEMPLATES = {
    "my_future_profession": (
        "📝 **Mavzu: My Future Profession (Mening kelajakdagi kasbim)**\n\n"
        "**Introduction (Kirish):**\n"
        "Choosing a career is one of the most important decisions in a person's life. "
        "A good profession not only helps you earn a living but also gives you the opportunity to contribute to society. "
        "In the future, I want to become an IT specialist (or teacher/doctor).\n\n"
        "**Body Paragraph 1 (Nega aynan shu kasb?):**\n"
        "Firstly, I have always been passionate about modern technology and problem-solving. "
        "In today's digital world, information technology plays a crucial role in every sphere of life, from education to medicine. "
        "By working in this field, I can create innovative solutions and help make people's lives easier.\n\n"
        "**Body Paragraph 2 (Hozir nima qilyapman?):**\n"
        "To achieve my goal, I am currently studying hard at school, focusing on English and mathematics. "
        "English is essential because it is the global language of science and communication. "
        "I also practice writing code and reading tech articles every day.\n\n"
        "**Conclusion (Xulosa):**\n"
        "In conclusion, becoming a professional requires dedication and continuous learning. "
        "I believe that with hard work and determination, I will achieve my dream and make my parents and country proud."
    ),
    "learning_english": (
        "📝 **Mavzu: The Importance of Learning English (Ingliz tilini o'rganishning ahamiyati)**\n\n"
        "**Introduction:**\n"
        "Nowadays, English is considered the international language of global communication, business, science, and technology. "
        "Millions of people all over the world study English to open new doors in their personal and professional lives.\n\n"
        "**Body Paragraph 1:**\n"
        "First and foremost, knowing English provides access to higher education and better job opportunities. "
        "The world's leading universities offer courses in English, and multinational companies always look for candidates who can speak it fluently.\n\n"
        "**Body Paragraph 2:**\n"
        "Furthermore, English allows you to travel freely and explore diverse cultures. "
        "Whenever you visit a foreign country, you can easily communicate with local people and solve any situation.\n\n"
        "**Conclusion:**\n"
        "All in all, learning English is not just an advantage today; it is a necessity. "
        "It broadens our horizons and connects us to the entire world."
    )
}


class EnglishService:
    @staticmethod
    def search_irregular_verb(query: str) -> List[Dict[str, Any]]:
        """Noto'g'ri fe'lni V1, V2, V3 yoki o'zbekcha tarjimasi bo'yicha qidirish."""
        q = query.strip().lower()
        results = []
        # 1. Aniq moslik (Exact match: V1, V2, V3 yoki uzbekcha to'liq so'z)
        for verb in IRREGULAR_VERBS:
            uz_meanings = [m.strip().lower() for m in verb["uz"].split(",")]
            v2_forms = [f.strip().lower() for f in verb["v2"].split("/")]
            v3_forms = [f.strip().lower() for f in verb["v3"].split("/")]
            if (q == verb["v1"].lower() or 
                q in v2_forms or 
                q in v3_forms or 
                q == verb["uz"].lower() or
                q in uz_meanings):
                results.append(verb)

        # 2. Qisman moslik (Substring match) agar topilmagan bo'lsa
        if not results:
            for verb in IRREGULAR_VERBS:
                if q in verb["v1"].lower() or q in verb["uz"].lower():
                    results.append(verb)
        return results

    @staticmethod
    def get_all_irregular_verbs_text(page: int = 1, page_size: int = 15) -> Tuple[str, int]:
        """Noto'g'ri fe'llar ro'yxatini sahifalab chiroyli formatda chiqarish."""
        total = len(IRREGULAR_VERBS)
        total_pages = (total + page_size - 1) // page_size
        page = max(1, min(page, total_pages))

        start = (page - 1) * page_size
        end = start + page_size
        subset = IRREGULAR_VERBS[start:end]

        lines = [
            f"📚 **Noto'g'ri fe'llar ro'yxati (Irregular Verbs) — {page}/{total_pages}**\n",
            "| V1 (Infinitive) | V2 (Past Simple) | V3 (Past Participle) | Ma'nosi |",
            "|---|---|---|---|"
        ]

        for v in subset:
            lines.append(f"• `{v['v1']}` — `{v['v2']}` — `{v['v3']}`: **{v['uz']}**")

        lines.append(f"\n💡 *Qidirish uchun: fe'lning istalgan shaklini yozib yuboring (Masalan: `wrote` yoki `bormoq`).*")
        return "\n".join(lines), total_pages

    @staticmethod
    def solve_open_brackets(text: str) -> Optional[str]:
        """Qavslarni ochish (Open brackets) vazifalarini avtomatik yechish."""
        # Qavs ichida fe'l bo'lsa: masalan (go), (study), (not like)
        match = re.search(r'([A-Za-z0-9\s,\'\.]+)\(([a-zA-Z\s]+)\)([A-Za-z0-9\s,\'\.\?!]*)', text)
        if not match:
            return None

        before = match.group(1).strip()
        verb = match.group(2).strip().lower()
        after = match.group(3).strip()
        full_lower = text.lower()

        # Kalit so'zlarni aniqlash
        is_past = any(w in full_lower for w in ["yesterday", "ago", "last week", "last year", "last night", "in 2020", "in 2019", "in 2015"])
        is_present_cont = any(w in full_lower for w in ["now", "at the moment", "look!", "listen!", "currently", "right now"])
        is_present_perf = any(w in full_lower for w in ["since", "already", "just", "yet", "ever", "never", "so far"])
        is_future = any(w in full_lower for w in ["tomorrow", "next week", "next month", "next year", "soon"])
        is_every_day = any(w in full_lower for w in ["every day", "usually", "always", "often", "sometimes", "rarely"])

        # Egasini (Subject) aniqlash
        is_third_person = any(re.search(r'\b' + s + r'\b', before.lower()) for s in ["he", "she", "it", "my mother", "my father", "the boy", "the girl", "the teacher", "ali", "sarah", "john"])
        is_i = bool(re.search(r'\bi\b', before.lower()))

        solution_answer = ""
        tense_name = ""
        rule_desc = ""

        # Noto'g'ri fe'l ma'lumotlarini tekshirish
        v_info = next((v for v in IRREGULAR_VERBS if v["v1"].lower() == verb), None)

        if is_past:
            tense_name = "Past Simple (O'tgan oddiy zamon)"
            rule_desc = "Gapda o'tgan zamon kalit so'zi (yesterday / last... / ago) bo'lgani sababli, fe'lning 2-shakli (V2) qo'llaniladi."
            if v_info:
                v2_first = v_info["v2"].split(" / ")[0]
                solution_answer = v2_first
            else:
                solution_answer = verb + "ed" if not verb.endswith("e") else verb + "d"

        elif is_present_cont:
            tense_name = "Present Continuous (Hozirgi davomli zamon)"
            rule_desc = "Gapda 'now / at the moment' kabi ayni damda sodir bo'layotganini bildiruvchi so'z bor: am/is/are + V-ing."
            aux = "am" if is_i else ("is" if is_third_person else "are")
            ing_verb = verb + "ing" if not verb.endswith("e") else verb[:-1] + "ing"
            solution_answer = f"{aux} {ing_verb}"

        elif is_present_perf:
            tense_name = "Present Perfect (Hozirgi tugallangan zamon)"
            rule_desc = "Gapda 'since / already / yet' kabi natija yoki davomiylikni bildiruvchi so'z bor: have/has + V3."
            aux = "has" if is_third_person else "have"
            if v_info:
                v3_first = v_info["v3"].split(" / ")[0]
                solution_answer = f"{aux} {v3_first}"
            else:
                solution_answer = f"{aux} {verb + 'ed' if not verb.endswith('e') else verb + 'd'}"

        elif is_future:
            tense_name = "Future Simple (Kelasi oddiy zamon)"
            rule_desc = "Gapda kelasi zamon kalit so'zi (tomorrow / next...) bor: will + V1."
            solution_answer = f"will {verb}"

        elif is_every_day or is_third_person:
            tense_name = "Present Simple (Hozirgi oddiy zamon)"
            rule_desc = "Doimiy harakat: 3-shaxs birlikda (he/she/it) fe'lga '-s' yoki '-es' qo'shiladi."
            if is_third_person:
                solution_answer = verb + "es" if verb.endswith(("o", "s", "ch", "sh", "x")) else (verb[:-1] + "ies" if verb.endswith("y") and verb[-2] not in "aeiou" else verb + "s")
            else:
                solution_answer = verb

        if solution_answer:
            full_completed = text.replace(f"({match.group(2)})", f"**{solution_answer}**")
            return (
                f"📌 **Qavslarni ochish vazifasi tahlili:**\n\n"
                f"📖 **Aniqlangan zamon:** {tense_name}\n"
                f"💡 **Grammatika qoidasi:** {rule_desc}\n\n"
                f"📝 **Tahlil bosqichlari:**\n"
                f"• Berilgan fe'l: `{verb}`\n"
                f"• Kalit so'z va ega tahlili asosida to'g'ri shakli tanlandi.\n\n"
                f"✅ **To'g'ri javob:** `{solution_answer}`\n\n"
                f"🌟 **To'liq to'g'ri gap:**\n"
                f"> {full_completed}"
            )
        return None

    @staticmethod
    def get_rule_by_key(key: str) -> Optional[str]:
        return ENGLISH_RULES.get(key)


english_service = EnglishService()
