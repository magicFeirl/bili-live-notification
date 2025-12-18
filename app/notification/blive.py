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

            media = [InputMediaPhoto(await streamer.download_cover())]

            await bot.send_media_group(
                user,
                media=media,
                caption=streamer.notification_text,
                disable_notification=streamer.silent,
            )
