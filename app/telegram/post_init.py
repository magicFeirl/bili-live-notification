from telegram import BotCommand
from telegram.ext import Application


async def register_command(application: Application):
    COMMANDS = [
        BotCommand("start", "start"),
        BotCommand("add", "添加直播间"),
        BotCommand("rm", "移除直播间"),
        BotCommand("ls", "查看直播间列表"),
        BotCommand("silent", "静音推送设置"),
        # BotCommand("help", "获取帮助"),
    ]

    bot = application.bot

    await bot.set_my_commands(COMMANDS)


async def post_init(application: Application):
    await register_command(application)
