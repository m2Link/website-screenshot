# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from config import Config
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from webshotbot import WebshotBot
from pyrogram import filters
import os


@WebshotBot.on_message(
    filters.regex(pattern="http[s]*://.+") & filters.private & ~filters.edited
)
async def checker(_, message: Message):
    msg = await message.reply_text("working", True)
    await msg.edit(
        text="Choose the prefered settings",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="🖼️Format - PDF", callback_data="format")],
                [InlineKeyboardButton(text="📃Page - Full", callback_data="page")],
                [InlineKeyboardButton(text="🖱Scroll Site - No", callback_data="scroll")],
                [
                    InlineKeyboardButton(
                        text="Show Additional Options🔽", callback_data="options"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Start ScreenShot📸", callback_data="render"
                    )
                ],
                [InlineKeyboardButton(text="✖️Cancel", callback_data="cancel")],
            ]
        ),
    )


@WebshotBot.on_message(filters.command(["start"]))
async def start(_, message: Message) -> None:
    await message.reply_text(
        f"<b>Hi {message.from_user.first_name} 👋\n"
        "I can take 📸 Screenshot of Website of a given link to either PDF or PNG/JPEG with many additional features. \n \nJust Send me link (must start with http(s)) to start capturing screenshot of website</b>",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("🧑‍💻Developer", url="https://t.me/ask_admin01")
             ],[
             InlineKeyboardButton("💬 Update Channel", url="https://t.me/m2botz"),
             InlineKeyboardButton("🗣 Support Group", url="https://t.me/m2botzsupport")
             ],[
             InlineKeyboardButton("😎About", callback_data="about_cb"),
             InlineKeyboardButton("🤔Help", callback_data="help_cb")]]
              
        ),
    )


@WebshotBot.on_message(filters.command(["about", "feedback"]))
async def feedback(_, message: Message) -> None:
    await message.reply_text(
        text="ABOUT ME \n Name :",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Channel🔰",
                        url="https://t.me/m2botz",
                    ), 
                    InlineKeyboardButton(
                        "Bug Report🐞",
                        url="https://t.me/m2botzsupport",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "Developer",
                        url="https://t.me/ask_admin01",
                    )
                ],
            ]
        ),
    )


@WebshotBot.on_message(filters.command(["debug", "log"]) & filters.private)
async def send_log(_, message: Message) -> None:
    try:
        sudo_user = int(os.environ["SUDO_USER"])
        if sudo_user != message.chat.id:
            raise Exception
    except Exception:
        return
    if os.path.exists("debug.log"):
        await message.reply_document("debug.log")
    else:
        await message.reply_text("file not found")

@WebshotBot.on_message(filters.command(["help"]))
async def help(_, message: Message) -> None:
    await message.reply_text(
        text="❓ How to use this bot \n \n➤ Send any link to me. \nNote: Link must start with http(s)\n \n➤ Select your preferred settings first. \n \n➤ Then Tap on Start ScreenShot 📸",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💬 Update Channel",
                        url="https://t.me/m2botz",
                    ),
                    InlineKeyboardButton(
                        "🗣 Support Group",
                        url="https://t.me/m2botzsupport",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🧑‍💻Developer",
                        url="https://t.me/ask_admin01",
                    )
                ],
            ]
        ),

