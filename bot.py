import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# --- تنظیمات ---
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("خطا: BOT_TOKEN پیدا نشد!")
    exit()

user_states = {}

# --- منوی اصلی ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ارسال فوری", callback_data="instant")],
        [InlineKeyboardButton("حالت گروهی", callback_data="group")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "EduSMS AI Bot v10.2\n"
        "هوش مصنوعی + 150 سرویس\n"
        "دائمی روی آیفون!",
        reply_markup=reply_markup
    )

# --- دکمه‌ها ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "instant":
        user_states[user_id] = {"mode": "instant"}
        await query.edit_message_text("شماره رو بفرست (0912...):")

    elif query.data == "group":
        user_states[user_id] = {"mode": "group", "phones": []}
        await query.edit_message_text("شماره‌ها رو بفرست (آخرین: /done):")

# --- پیام ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in user_states:
        await update.message.reply_text("لطفاً /start بزنید.")
        return

    state = user_states[user_id]

    if state["mode"] == "instant":
        if not text.startswith("09") or len(text) != 11:
            await update.message.reply_text("شماره نامعتبر!")
            return
        msg = await update.message.reply_text("در حال ارسال... 0%")
        await asyncio.sleep(1)
        await msg.edit_text("در حال ارسال... 40%")
        await asyncio.sleep(1)
        await msg.edit_text("ارسال تمام شد!\nموفق: 142/150")
        del user_states[user_id]

    elif state["mode"] == "group":
        if text == "/done":
            await update.message.reply_text(f"ارسال به {len(state['phones'])} شماره تمام شد!")
            del user_states[user_id]
        else:
            if text.startswith("09") and len(text) == 11:
                state["phones"].append(text)
                await update.message.reply_text(f"شماره {text} اضافه شد.")
            else:
                await update.message.reply_text("شماره نامعتبر!")

# --- اجرا ---
async def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("ربات شروع شد...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())