from aiogram import Router, F, Bot
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)
from aiogram.filters import Command

import database as db
from locales import t
from config import PREMIUM_PLANS, STARS_PACKAGES


router = Router()


# Bannerlar
PREMIUM_BANNER = "assets/banner_premium.png"
STARS_BANNER = "assets/banner_stars.png"


async def safe_edit(
    callback: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None
):
    try:
        await callback.message.edit_text(
            text,
            reply_markup=keyboard
        )

    except Exception:
        try:
            await callback.message.delete()
        except Exception:
            pass

        await callback.message.answer(
            text,
            reply_markup=keyboard
        )


def back_button(
    lang: str,
    to: str = "menu_back"
):
    return InlineKeyboardButton(
        text=t(lang, "btn_back"),
        callback_data=to
    )


def _grid(buttons: list, columns: int = 2):
    return [
        buttons[i:i + columns]
        for i in range(0, len(buttons), columns)
    ]


def premium_keyboard(lang: str):

    items = [
        InlineKeyboardButton(
            text=t(
                lang,
                "premium_item",
                months=p["months"],
                price=f'{p["price_som"]:,}'.replace(",", " ")
            ),
            callback_data=f"premplan_{p['id']}"
        )

        for p in PREMIUM_PLANS
    ]

    rows = _grid(items, 2)

    rows.append([
        back_button(lang)
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


def premium_type_keyboard(
    lang: str,
    plan_id: str
):

    self_allowed = plan_id in (
        "prem_1m",
        "prem_12m"
    )

    if self_allowed:
        rows = [
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_gift"),
                    callback_data=f"gprem_{plan_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_self"),
                    callback_data=f"sprem_{plan_id}"
                )
            ]
        ]

    else:
        rows = [
            [
                InlineKeyboardButton(
                    text=t(lang, "btn_buy_premium"),
                    callback_data=f"gprem_{plan_id}"
                )
            ]
        ]


    rows.append([
        back_button(
            lang,
            "menu_premium"
        )
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )def stars_keyboard(lang: str):

    items = [
        InlineKeyboardButton(
            text=t(
                lang,
                "stars_item",
                amount=s["amount"],
                price=f'{s["price_som"]:,}'.replace(",", " ")
            ),
            callback_data=f"buy_star_{s['id']}"
        )

        for s in STARS_PACKAGES
    ]

    rows = _grid(items, 2)

    rows.append([
        back_button(lang)
    ])

    return InlineKeyboardMarkup(
        inline_keyboard=rows
    )


async def build_orders_text(
    lang: str,
    user_id: int
):

    orders = await db.get_user_orders(user_id)

    if not orders:
        return t(lang, "no_orders")


    status_map = {
        "pending": "status_pending",
        "paid": "status_paid",
        "rejected": "status_rejected"
    }


    lines = [
        t(lang, "your_orders")
    ]


    for order_id, item, price, status in orders:

        lines.append(
            t(
                lang,
                "order_line",
                id=order_id,
                item=item,
                price=f"{price:,}".replace(",", " "),
                status=t(
                    lang,
                    status_map.get(
                        status,
                        "status_pending"
                    )
                )
            )
        )


    return "\n".join(lines)



@router.callback_query(F.data == "menu_premium")
async def show_premium(callback: CallbackQuery):

    lang = await db.get_lang(
        callback.from_user.id
    )


    try:
        await callback.message.delete()
    except Exception:
        pass


    photo = FSInputFile(
        PREMIUM_BANNER
    )


    await callback.message.answer_photo(
        photo,
        caption=t(
            lang,
            "choose_premium"
        ),
        reply_markup=premium_keyboard(lang)
    )


    await callback.answer()



@router.callback_query(F.data == "menu_stars")
async def show_stars(callback: CallbackQuery):

    lang = await db.get_lang(
        callback.from_user.id
    )


    try:
        await callback.message.delete()
    except Exception:
        pass


    photo = FSInputFile(
        STARS_BANNER
    )


    await callback.message.answer_photo(
        photo,
        caption=t(
            lang,
            "choose_stars"
        ),
        reply_markup=stars_keyboard(lang)
    )


    await callback.answer()



@router.callback_query(F.data.startswith("premplan_"))
async def show_premium_type_choice(
    callback: CallbackQuery
):

    lang = await db.get_lang(
        callback.from_user.id
    )


    plan_id = callback.data.replace(
        "premplan_",
        ""
    )


    plan = next(
        (
            p for p in PREMIUM_PLANS
            if p["id"] == plan_id
        ),
        None
    )


    if not plan:
        await callback.answer(
            "Xatolik / Error",
            show_alert=True
        )
        return


    text = (
        t(
            lang,
            "premium_choice_title",
            months=plan["months"]
        )
        + "\n\n"
    )


    if plan_id in (
        "prem_1m",
        "prem_12m"
    ):

        text += (
            t(lang, "premium_choice_gift_desc")
            +
            t(lang, "premium_choice_self_desc")
        )

    else:

        text += t(
            lang,
            "premium_choice_buy_desc"
        )


    await safe_edit(
        callback,
        text,
        premium_type_keyboard(
            lang,
            plan_id
        )
    )


    await callback.answer()@router.callback_query(F.data == "menu_orders")
async def show_orders(callback: CallbackQuery):

    lang = await db.get_lang(
        callback.from_user.id
    )

    text = await build_orders_text(
        lang,
        callback.from_user.id
    )


    await safe_edit(
        callback,
        text,
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    back_button(lang)
                ]
            ]
        )
    )


    await callback.answer()



@router.message(Command("premium"))
async def cmd_premium(message: Message):

    lang = await db.get_lang(
        message.from_user.id
    )


    photo = FSInputFile(
        PREMIUM_BANNER
    )


    await message.answer_photo(
        photo,
        caption=t(
            lang,
            "choose_premium"
        ),
        reply_markup=premium_keyboard(lang)
    )



@router.message(Command("stars"))
async def cmd_stars(message: Message):

    lang = await db.get_lang(
        message.from_user.id
    )


    photo = FSInputFile(
        STARS_BANNER
    )


    await message.answer_photo(
        photo,
        caption=t(
            lang,
            "choose_stars"
        ),
        reply_markup=stars_keyboard(lang)
    )



@router.message(Command("orders"))
async def cmd_orders(message: Message):

    lang = await db.get_lang(
        message.from_user.id
    )


    text = await build_orders_text(
        lang,
        message.from_user.id
    )


    await message.answer(
        text
    )



@router.message(Command("language"))
async def cmd_language(message: Message):

    from handlers.start import lang_keyboard


    await message.answer(
        t("uz", "choose_lang"),
        reply_markup=lang_keyboard()
        )
