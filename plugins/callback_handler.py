# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from helper import mediagroup_gen, split_image
from plugins.command_handler import (
    feedback,
)
from helper.printer import Printer
from webshotbot import WebshotBot
from pyrogram import filters
from config import Config
import asyncio


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "render"))
async def primary_cb(client: WebshotBot, callback_query: CallbackQuery):
    await callback_query.answer("processing your request")
    message = await callback_query.message.edit("**processing...**")
    printer = Printer.from_message(callback_query.message)
    printer.allocate_folder(
        callback_query.message.chat.id, callback_query.message.message_id
    )
    await message.edit("**Please Wait...**")
    try:
        future, wait_event = client.new_request(printer, callback_query.message.chat.id)
        await wait_event.wait()
        await message.edit(
            "**📸 Screenshot the Website...**",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Render Now", "release")]]
            )
            if printer.scroll_control == "manual"
            else None,
        )
        if Config.LOG_GROUP is not None:
            await client.send_message(
                Config.LOG_GROUP,
                printer._get_logstr(
                    callback_query.message.reply_to_message.from_user.id,
                    callback_query.message.reply_to_message.from_user.first_name,
                ),
            )
        await future
    except Exception as e:
        await message.edit(f"`{e}`")
        printer.cleanup()
        return
    await message.edit("**uploading...**")
    if printer.split and printer.fullpage:
        loc_of_images = await asyncio.get_event_loop().run_in_executor(
            None, split_image, printer.file
        )
        for media_group in mediagroup_gen(loc_of_images):
            await asyncio.gather(
                callback_query.message.reply_chat_action("upload_photo"),
                callback_query.message.reply_media_group(
                    media_group, disable_notification=True
                ),
            )
    elif printer.type == "pdf" or printer.fullpage:
        await asyncio.gather(
            callback_query.message.reply_chat_action("upload_document"),
            callback_query.message.reply_document(printer.file),
        )
    elif not printer.fullpage:
        await asyncio.gather(
            callback_query.message.reply_chat_action("upload_photo"),
            callback_query.message.reply_photo(printer.file),
        )
    await asyncio.gather(
        message.delete(),
        message.reply_text(
            '__Please toggle "Scroll Site" setting if the output has no content.__'
        ),
    )
    printer.cleanup()


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "release"))
async def release_cb(client: WebshotBot, callback_query: CallbackQuery):
    event = client.get_request(callback_query.message.chat.id)
    if event is not None:
        event.set()
        await callback_query.answer("rendering now")
        await callback_query.message.edit_reply_markup(None)
    else:
        await callback_query.answer("please wait")


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "statics"))
async def statics_cb(client: WebshotBot, callback_query: CallbackQuery):
    await callback_query.answer("processing")
    printer = Printer("statics", callback_query.message.reply_to_message.text)
    message = await callback_query.message.edit("**please wait you are in a queue...**")
    try:
        future, wait_event = client.new_request(printer)
        await wait_event.wait()
        await asyncio.gather(message.edit("**rendering the statics...**"), future)
        await asyncio.gather(
            callback_query.message.reply_chat_action("upload_document"),
            callback_query.message.reply_document(printer.file),
        )
        await message.delete()
    except Exception as e:
        await message.edit(f"`{e}`")
    finally:
        printer.cleanup()  # type: ignore


@WebshotBot.on_callback_query()
async def keyboards_cb(_, callback_query: CallbackQuery):
    cb_data = callback_query.data
    msg = callback_query.message
    if not cb_data == "cancel":
        # cause @Spechide said so
        await callback_query.answer()
    if cb_data == "splits":
        current_boolean = msg.reply_markup.inline_keyboard[-4][0]
        msg.reply_markup.inline_keyboard[-4][0]["text"] = (
            "Split - No" if "Yes" in current_boolean.text else "Split - Yes"
        )
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "page":
        current_page = msg.reply_markup.inline_keyboard[1][0]
        msg.reply_markup.inline_keyboard[1][0]["text"] = (
            "Page - Partial" if "Full" in current_page.text else "Page - Full"
        )
        await msg.edit(
            text="Choose the prefered Settings ⚙️ \n \n➤ Tap on Format to toggle among PDF, PNG & JPEG \n➤ Tap on Page to toggle between Full & Partial \n➤ Tap on Scroll Site to enable scrolling \n \nAfter Chosen Settings, Tap on Start Screenshot 📸", reply_markup=msg.reply_markup
        )

    elif cb_data == "scroll":
        current_load = msg.reply_markup.inline_keyboard[2][0]
        if "No" in current_load.text:
            text = "Auto"
        elif "Auto" in current_load.text:
            text = "Manual"
        elif "Manual" in current_load.text:
            text = "No"
        msg.reply_markup.inline_keyboard[2][0].text = f"Scroll Site - {text}"
        await msg.edit(
            text="Choose the prefered Settings ⚙️ \n \n➤ Tap on Format to toggle among PDF, PNG & JPEG \n➤ Tap on Page to toggle between Full & Partial \n➤ Tap on Scroll Site to enable scrolling \n \nAfter Chosen Settings, Tap on Start Screenshot 📸", reply_markup=msg.reply_markup
        )

    elif cb_data == "options":
        current_option = msg.reply_markup.inline_keyboard[3][0].text
        current_format = msg.reply_markup.inline_keyboard[0][0].text
        options_to_change = (
            "Hide Additional Options🔼"
            if "show" in current_option
            else "Show Additional Options🔽"
        )
        if "hide" in options_to_change:
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [
                    InlineKeyboardButton(
                        text="resolution | 800x600", callback_data="res"
                    )
                ],
            )
            if "PDF" not in current_format:
                msg.reply_markup.inline_keyboard.insert(
                    -2,
                    [InlineKeyboardButton(text="Split - No", callback_data="splits")],
                )
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [
                    InlineKeyboardButton(
                        text="▫️ Site Statitics ▫️", callback_data="statics"
                    )
                ],
            )
        else:
            for _ in range((2 if "PDF" in current_format else 3)):
                msg.reply_markup.inline_keyboard.pop(-3)
        msg.reply_markup.inline_keyboard[3][0]["text"] = options_to_change
        await msg.edit(
            text="Choose the prefered Settings ⚙️ \n \n➤ Tap on Format to toggle among PDF, PNG & JPEG \n➤ Tap on Page to toggle between Full & Partial \n➤ Tap on Scroll Site to enable scrolling \n \nAfter Chosen Settings, Tap on Start Screenshot 📸", reply_markup=msg.reply_markup
        )

    elif cb_data == "res":
        current_res = msg.reply_markup.inline_keyboard[4][0].text
        if "800" in current_res:
            res_to_change = "resolution | 1280x720"
        elif "1280" in current_res:
            res_to_change = "resolution | 2560x1440"
        elif "2560" in current_res:
            res_to_change = "resolution | 640x480"
        else:
            res_to_change = "resolution | 800x600"
        msg.reply_markup.inline_keyboard[4][0]["text"] = res_to_change
        await msg.edit(
            text="Choose the prefered Settings ⚙️ \n \n➤ Tap on Format to toggle among PDF, PNG & JPEG \n➤ Tap on Page to toggle between Full & Partial \n➤ Tap on Scroll Site to enable scrolling \n \nAfter Chosen Settings, Tap on Start Screenshot 📸", reply_markup=msg.reply_markup
        )

    elif cb_data == "format":
        current_format = msg.reply_markup.inline_keyboard[0][0]
        if "PDF" in current_format.text:
            format_to_change = "Format - PNG"
            if "hide" in msg.reply_markup.inline_keyboard[3][0].text:
                msg.reply_markup.inline_keyboard.insert(
                    -3,
                    [InlineKeyboardButton(text="Split - No", callback_data="splits")],
                )
        elif "PNG" in current_format.text:
            format_to_change = "Format - JPEG"
        elif "JPEG" in current_format.text:
            format_to_change = "Format - PDF"
            if "hide" in msg.reply_markup.inline_keyboard[3][0].text:
                msg.reply_markup.inline_keyboard.pop(-4)
        msg.reply_markup.inline_keyboard[0][0]["text"] = format_to_change
        await msg.edit(
            text="Choose the prefered Settings ⚙️ \n \n➤ Tap on Format to toggle among PDF, PNG & JPEG \n➤ Tap on Page to toggle between Full & Partial \n➤ Tap on Scroll Site to enable scrolling \n \nAfter Chosen Settings, Tap on Start Screenshot 📸", reply_markup=msg.reply_markup
        )

    elif cb_data == "cancel":
        await callback_query.answer("Canceled your request..!")
        await msg.delete()

    elif cb_data == "about_cb":
        await msg.delete()
        await feedback(_, msg)
