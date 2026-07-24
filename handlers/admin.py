from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

import database as db
from locales import t
from config import ADMIN_IDS

router = Router()


@router.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def handle_order_decision(callback: CallbackQuery, bot: Bot):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("Sizga ruxsat yo'q / No permission", show_alert=True)
        return

    action, order_id_str = callback.data.split("_")
    order_id = int(order_id_str)
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Buyurtma topilmadi", show_alert=True)
        return

    _, user_id, item, price, method, status = order
    new_status = "paid" if action == "approve" else "rejected"
    await db.update_order_status(order_id, new_status)

    user_lang = await db.get_lang(user_id)
    text_key = "order_approved" if action == "approve" else "order_rejected"
    await bot.send_message(user_id, t(user_lang, text_key, order_id=order_id))

    result_text = "✅ TASDIQLANDI" if action == "approve" else "❌ RAD ETILDI"
    try:
        await callback.message.edit_caption(caption=f"{callback.message.caption}\n\n{result_text}")
    except Exception:
        pass
    await callback.answer("Bajarildi ✅")
