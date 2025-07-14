import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = "7566837278:AAEDBWzXtqk21JzTRbYewZAKtpi5apEcx1s"
TARGET_GROUP_ID = -1002854526884  # Private guruh ID

def escape_html(text):
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
    )

async def delete_message_quick(chat_id, message_id, context):
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        print(f"❗ Xabarni o‘chirishda xatolik: {e}")

async def forward_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.from_user:
        return

    user = message.from_user
    first_name = escape_html(user.first_name or "Foydalanuvchi")
    text = escape_html(message.text or "")

    # Link ko‘rinishi
    if user.username:
        user_display = f"<a href='https://t.me/{user.username}'>{first_name}</a>"
    else:
        user_display = f"<a href='tg://user?id={user.id}'>{first_name}</a>"

    final_text = f"👤 Yo‘lovchi: {user_display}\n✉️ Xabar: {text}"

    chat_type = update.effective_chat.type

    if chat_type in ['group', 'supergroup']:
        # Public guruhdan xabar keldi

        # Darhol o‘chirishni boshlaymiz
        asyncio.create_task(delete_message_quick(message.chat_id, message.message_id, context))

        # Private guruhga yuboramiz
        try:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=final_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"❗ Yuborishda xatolik: {e}")

        # Foydalanuvchiga javob beramiz
        try:
            javob = f"Hurmatli {first_name}, xabaringiz qabul qilindi. Haydovchilar tez orada siz bilan bogʻlanishadi."
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=javob
            )
        except Exception as e:
            print(f"❗ Javob yozishda xatolik: {e}")

    elif chat_type == 'private':
        # Botga private chatdan kelgan xabarni private guruhga yuborish

        try:
            await context.bot.send_message(
                chat_id=TARGET_GROUP_ID,
                text=final_text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f"❗ Yuborishda xatolik: {e}")

        # Javob beramiz
        try:
            javob = f"Hurmatli {first_name}, xabaringiz qabul qilindi. Tez orada javob olasiz."
            await context.bot.send_message(
                chat_id=message.chat_id,
                text=javob
            )
        except Exception as e:
            print(f"❗ Javob yozishda xatolik: {e}")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, forward_group_message))

print("🤖 Bot ishga tushdi. Guruh va private chatdan xabarlarni qabul qiladi.")
app.run_polling()
