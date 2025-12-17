from functools import wraps
from textwrap import dedent

from telegram import Update, InputMediaPhoto
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from telegram.constants import ParseMode

from app.db.models import Streamer
from app.telegram.post_init import post_init
import config


def allowed_user(func):
    """
    用户鉴权 - 仅允许指定 ID 的用户使用 bot
    """

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user_id = update.effective_user.id
        if user_id not in config.ADMIN_USERS:
            return
        return await func(update, context, *args, **kwargs)

    return wrapper


@allowed_user
async def start_helper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "这是一个B 站直播推送 bot\n输入 /add 开始添加监听用户"

    await update.message.reply_text(text)


@allowed_user
async def add_streamer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    指令: /add <room_id>
    示例: /add 1001
    """
    args = context.args
    if len(args) != 1:
        await update.message.reply_text(
            "❌ 格式错误。\n用法: /add <直播间ID>\n或批量添加 /add <ID1>, <ID2>, ..."
        )
        return

    try:
        user = Streamer.find_one(int(args[0]))
        if not user:
            message = await update.message.reply_text("开始获取直播间信息...")
            # 获取并保存主播信息
            await user.update_streamer_from_bilibili(username=True)
            user.create()

            cover_media = [InputMediaPhoto(await user.download_cover())]

            await update.message.reply_media_group(
                cover_media,
                caption=f"✅ 已添加直播间：\n{user.info}",
                parse_mode=ParseMode.HTML,
            )
            await message.delete()
        else:
            await update.message.reply_text(
                f"⚠️ 直播间已存在\n{user.info}", parse_mode=ParseMode.HTML
            )
    except ValueError:
        await update.message.reply_text("❌ 直播间ID 必须是数字。")


@allowed_user
async def rm_streamer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    指令: /rm <room_id>
    示例: /rm 1001
    """
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("❌ 格式错误。\n用法: /rm <直播间ID>")
        return

    try:
        user = Streamer.find_one(int(args[0]))

        if not user:
            await update.message.reply_text(f"⚠️ 找不到直播间: {user.room_id}")
            return

        user.delete()

        await update.message.reply_text(
            f"🗑️ 已移除主播: {user.info}", parse_mode=ParseMode.HTML
        )
    except ValueError:
        await update.message.reply_text("❌ 主播ID 必须是数字。")


async def ls_streamer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    指令: /ls
    列出当前监听列表
    """

    streamers = Streamer.all()

    if not streamers:
        await update.message.reply_text("📭 当前监控列表为空。")
        return

    lines = []

    for streamer in streamers:
        line = f"{streamer.name} {streamer.room_id}\n{streamer.status_text} | {streamer.silent_text}\n"
        lines.append(line)

    msg = f"""
    当前监听列表:\n\n{"\n\n".join(lines)}
    """

    await update.message.reply_text(dedent(msg))


@allowed_user
async def set_silent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    指令: /silent <uid>
    切换静音状态 (0 -> 1, 1 -> 0)
    """
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("❌ 格式错误。\n用法: /silent <房间号>")
        return

    try:
        user = Streamer.find_one(room_id=int(args[0]))

        if not user:
            await update.message.reply_text(f"⚠️ 找不到房间: {user.room_id}")
            return

        silent = not user.silent
        user.update({"silent": silent})

        status_text = "🔕 已开启静音" if silent else "🔔 已关闭静音"
        await update.message.reply_text(f"⚙️ 设置成功:\n\n {user.name} - {status_text}")
    except ValueError:
        await update.message.reply_text("❌ 主播ID 必须是数字。")


def run_polling():
    TOKEN = config.BOT_TOKEN

    application = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start_helper))
    application.add_handler(CommandHandler("add", add_streamer))
    application.add_handler(CommandHandler("rm", rm_streamer))
    application.add_handler(CommandHandler("ls", ls_streamer))
    application.add_handler(CommandHandler("silent", set_silent))

    print("Running...")
    application.run_polling()
