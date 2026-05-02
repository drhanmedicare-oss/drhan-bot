"""
Telegram FAQ Bot - Dr. Han Medical
"""

import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
)

# ─── CONFIG ───────────────────────────────────────────────────────────────────

BOT_TOKEN = "8699169284:AAG9XGBf84zyqKxNd07rMk_I4mKsjyHOYvw"

# ─── QR CODE PHOTO FILE IDs သို့မဟုတ် PATH ────────────────────────────────────
# မင်းရဲ့ QR code ပုံတွေ ထည့်ချင်ရင် ဒီနေရာမှာ file path ပြောင်းပါ
QR_CODES = {
    "kpay":  "qr_kpay.jpg",   # KPay QR code ပုံဖိုင်
    "wave":  "qr_wave.jpg",   # Wave Pay QR code ပုံဖိုင်
    "aya":   "qr_aya.jpg",    # AYA Pay QR code ပုံဖိုင်
    "uab":   "qr_uab.jpg",    # UAB Pay QR code ပုံဖိုင်
}

# ─── FAQ DATA ─────────────────────────────────────────────────────────────────

FAQ_DATA = [
    {
        "keywords": ["နာရီ", "ဖွင့်", "ပိတ်", "ဘယ်အချိန်", "working hours", "open", "close"],
        "answer": (
            "🕐 *ဖွင့်ချိန်/ပိတ်ချိန်*\n"
            "တနင်္လာ - သောကြာ: မနက် ၉နာရီ - ညနေ ၆နာရီ\n"
            "စနေ: မနက် ၉နာရီ - မွန်းတည့် ၁၂နာရီ\n"
            "တနင်္ဂနွေ: ပိတ်ရက်"
        ),
    },
    {
        "keywords": ["နေရာ", "address", "location", "လိပ်စာ", "ဘယ်မှာ", "ရောက်", "လာ"],
        "answer": (
            "📍 *လိပ်စာ*\n"
            "Online ဆေးခန်း — Telegram မှတဆင့် ဝန်ဆောင်မှုပေးပါသည်\n\n"
            "💬 @drhanmedical သို့ တိုက်ရိုက် ဆက်သွယ်နိုင်ပါသည်"
        ),
    },
    {
        "keywords": ["ဈေးနှုန်း", "price", "စျေး", "ဘယ်လောက်", "cost", "rate", "ကြေး"],
        "answer": (
            "💰 *ဈေးနှုန်းများ*\n"
            "🩺 Online Consultation — ၅,၀၀၀ ကျပ်\n"
            "📋 ဆေးညွှန်းထုတ်ပေးခြင်း — ပါဝင်ပြီး\n"
            "💊 ဆေးတောင်းမှု လမ်းညွှန် — အခမဲ့\n\n"
            "အသေးစိတ်အတွက် /contact မှာ ဆက်သွယ်ပါ။"
        ),
    },
    {
        "keywords": ["ဆက်သွယ်", "contact", "ဖုန်း", "phone", "email", "viber"],
        "answer": (
            "📞 *ဆက်သွယ်ရန်*\n"
            "💬 Telegram: @drhanmedical\n"
            "📱 Phone/Viber: 09-XXXXXXXXX"
        ),
    },
    {
        "keywords": ["consult", "စစ်", "ဆေးစစ်", "မေး", "online"],
        "answer": (
            "🩺 *Online Consultation*\n"
            "Bot မှတဆင့် မေးမြန်းပါ။\n"
            "ဆရာဝန်မှ ၂၄ နာရီအတွင်း ပြန်ဆက်သွယ်ပေးမည်။\n\n"
            "💬 @drhanmedical သို့ တိုက်ရိုက် ဆက်သွယ်နိုင်ပါသည်"
        ),
    },
    {
        "keywords": ["payment", "ငွေပေး", "ငွေချေ", "kpay", "wave", "ဘဏ်", "ငွေ", "pay", "ကျပ်"],
        "answer": "💳 *ငွေပေးချေမှု*\nငွေပေးချေလိုသော နည်းလမ်းကို ရွေးချယ်ပါ 👇",
        "payment": True,
    },
]

DEFAULT_ANSWER = (
    "❓ တောင်းပန်ပါတယ်၊ ဒီမေးခွန်းကို နားမလည်ပါ။\n\n"
    "ဒီ command တွေ သုံးနိုင်ပါတယ်:\n"
    "/faq - မေးခွန်းအားလုံး ကြည့်ရန်\n"
    "/contact - ဆက်သွယ်ရန်"
)

# ─── KEYBOARD ─────────────────────────────────────────────────────────────────

QUICK_REPLIES = [
    ["ဖွင့်ချိန် ⏰", "လိပ်စာ 📍"],
    ["ဈေးနှုန်း 💰", "ဆေးစစ်ရန် 🩺"],
    ["ငွေပေးချေမှု 💳", "ဆက်သွယ်ရန် 📞"],
]

def get_keyboard():
    return ReplyKeyboardMarkup(QUICK_REPLIES, resize_keyboard=True)

def get_payment_keyboard():
    keyboard = [
        [InlineKeyboardButton("💜 KPay", callback_data="qr_kpay"),
         InlineKeyboardButton("🔵 Wave Pay", callback_data="qr_wave")],
        [InlineKeyboardButton("🟣 AYA Pay", callback_data="qr_aya"),
         InlineKeyboardButton("🔴 UAB Pay", callback_data="qr_uab")],
    ]
    return InlineKeyboardMarkup(keyboard)

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def find_faq(text: str):
    text_lower = text.lower()
    for item in FAQ_DATA:
        for keyword in item["keywords"]:
            if keyword.lower() in text_lower:
                return item
    return None

# ─── HANDLERS ─────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "သူငယ်ချင်း"
    # ပုံအရင်ပို့
    with open("img/stic.png", "rb") as photo:
        await update.message.reply_photo(photo=photo)
    # ပြီးမှ စာပို့
    await update.message.reply_text(
        f"မင်္ဂလာပါ {name}! 🙏\n\n"
        "Dr. Han Medical Online ဆေးခန်းသို့ ကြိုဆိုပါတယ်။\n\n"
        "ဘာများ သိချင်လဲ ရွေးချယ်ပါ သို့မဟုတ် မေးလိုတာ ရိုက်ပါ။",
        reply_markup=get_keyboard(),
        parse_mode="Markdown",
    )

async def faq_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "📋 *မကြာခဏ မေးလေ့ရှိသော မေးခွန်းများ*\n\n"
        "• ဖွင့်ချိန်/ပိတ်ချိန်\n"
        "• လိပ်စာ/တည်နေရာ\n"
        "• ဈေးနှုန်းများ\n"
        "• Online ဆေးစစ်ရန်\n"
        "• ဆက်သွယ်ရန်\n"
        "• ငွေပေးချေမှု\n\n"
        "ဒီ topic တွေ ရိုက်မေးနိုင်ပါတယ်!"
    )
    await update.message.reply_text(msg, reply_markup=get_keyboard(), parse_mode="Markdown")

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📞 *ဆက်သွယ်ရန်*\n"
        "💬 Telegram: @drhanmedical\n"
        "📱 Phone/Viber: 09-XXXXXXXXX",
        reply_markup=get_keyboard(),
        parse_mode="Markdown",
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    faq = find_faq(text)

    if faq is None:
        await update.message.reply_text(DEFAULT_ANSWER, reply_markup=get_keyboard())
        return

    # ငွေပေးချေမှု — inline button ပြပါ
    if faq.get("payment"):
        await update.message.reply_text(
            faq["answer"],
            reply_markup=get_payment_keyboard(),
            parse_mode="Markdown",
        )
    else:
        await update.message.reply_text(
            faq["answer"],
            reply_markup=get_keyboard(),
            parse_mode="Markdown",
        )

async def handle_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    qr_map = {
    "qr_kpay": ("💜 KPay QR Code", "img/han.png"),
    "qr_wave": ("🔵 Wave Pay QR Code", "img/han.png"),
    "qr_aya":  ("🟣 AYA Pay QR Code", "img/han.png"),
    "qr_uab":  ("🔴 UAB Pay QR Code", "img/han.png"),
}

    label, filename = qr_map.get(query.data, ("QR Code", ""))

    try:
        with open(filename, "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=f"{label}\n\nပေးချေပြီးပါက screenshot ရိုက်ပြီး @drhanmedical သို့ ပေးပို့ပါ။",
            )
    except FileNotFoundError:
        await query.message.reply_text(
            f"{label}\n\n⚠️ QR code ပုံဖိုင် မတွေ့ပါ။\nဆရာဝန်ထံ တိုက်ရိုက် ဆက်သွယ်ပါ — @drhanmedical"
        )

# ─── MAIN ─────────────────────────────────────────────────────────────────────

async def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("faq", faq_list))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CallbackQueryHandler(handle_qr, pattern="^qr_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("✅ Dr. Han Medical Bot စတင်လည်ပတ်နေပါပြီ...")

    async with app:
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())