"""B站开播检查定时任务"""

from dataclasses import asdict


from telegram import Bot, InputMediaPhoto

from app.db.models import Streamer
import config


async def is_diff_live_status(streamer: Streamer):
    """ """
    current_status = streamer.status
    streamer = await streamer.update_streamer_from_bilibili()

    if streamer.status != current_status:
        return streamer


async def notification():
    bot = Bot(config.BOT_TOKEN)

    for user in config.ADMIN_USERS:
        for streamer in Streamer.all():
            # 找出当前直播状态 != 上次直播状态的直播间
            current_status = streamer.status

            try:
                streamer = await streamer.update_streamer_from_bilibili()
            except Exception:
                continue

            print(streamer.name, current_status, streamer.status)

            if streamer.status == current_status:
                continue

            streamer.update(asdict(streamer))

            from telegram import InlineKeyboardButton, InlineKeyboardMarkup

            room_id = streamer.room_id
            btn_h5 = InlineKeyboardButton(
                text="看！", url=f"https://live.bilibili.com/h5/{room_id}"
            )

            keyboard = [[btn_h5]]

            reply_markup = InlineKeyboardMarkup(keyboard)

            # 仅开播显示观看按钮
            await bot.send_photo(
                user,
                photo=await streamer.download_cover(),
                caption=streamer.notification_text,
                disable_notification=streamer.silent,
                reply_markup=reply_markup if streamer.status else None,
            )
