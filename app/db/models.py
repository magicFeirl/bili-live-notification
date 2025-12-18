from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
from textwrap import dedent

from .sql import streamer_table
from app.bilibili import live


@dataclass
class Streamer:
    """
    对应主播信息表
    """

    room_id: int  # 房间ID

    id: Optional[int] = None
    uid: int = -1  # 主播 ID
    name: str = ""  # 主播名
    title: str = ""  # 直播标题，默认为空
    cover_url: Optional[str] = None  # 封面 URL，可能为空

    status: int = 0  # 0 or 1 是否开播中，默认 0 (未开播)
    live_start: Optional[datetime] = None  # 开播时间
    live_end: Optional[datetime] = None  # 下播时间

    is_delete: bool = False  # 是否被标记删除，默认 False
    silent: bool = False  # 是否静音推送

    async def update_streamer_from_bilibili(self, username=False):
        """调用接口，原地更新主播信息
        :param username:  是否获取用户名信息
        """

        response = await self.get_room_info()
        data = response.get("data", {})

        # 映射直播状态 (B站: 1为直播中)
        self.status = 1 if data.get("live_status") == 1 else 0

        # 映射基本信息
        self.title = data.get("title", "")
        self.cover_url = data.get("user_cover")
        self.uid = data.get("uid")

        # 获取用户名
        if username:
            user_info = (await self.get_user_info())["data"]
            self.name = user_info["info"]["uname"]

        # 映射开播时间
        live_time_str = data.get("live_time", "0000-00-00 00:00:00")
        if self.status == 1:
            try:
                self.live_start = datetime.strptime(live_time_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                pass
        else:
            self.live_start = None

        return self

    @property
    def info(self):
        """用户信息文本"""
        s = f"""
       {self.name}
       UID: <code>{self.uid}</code>
       ROOM ID: <code>{self.room_id}</code>
        """

        return dedent(s)

    @property
    def status_text(self):
        return "🟢 直播中" if self.status == 1 else "🔴 未开播"

    @property
    def silent_text(self):
        return "🔕 静音" if self.silent else "🔔 提醒"

    @property
    def notification_text(self):
        status_icon = '🟢' if self.status else '🔴'
        status_action = '开' if self.status else '下' 
        
        """开播通知文本"""
        s = f"""
        {status_icon} #{self.name} {status_action}播了

        📺 标题：{self.title}
        ⏰ 时间：{self.live_start}
        """

        return dedent(s)

    @staticmethod
    def all():
        streamers = [Streamer(**row) for row in streamer_table.find(is_delete=False)]
        return streamers

    @staticmethod
    def find_one(room_id):
        row = streamer_table.find_one(room_id=room_id, is_delete=False)
        return Streamer(**row) if row else None

    async def download_cover(self):
        if not self.cover_url:
            self.cover_url = "https://i1.hdslb.com/bfs/archive/b77d81bc138419fb65d9b0a35c400bfd2b55ac55.jpg@260w_160h.webp"

        return await live.download_assets(self.cover_url)

    async def get_user_info(self):
        """获取用户信息"""
        user_info = await live.get_room_master_info(self.uid)
        return user_info

    async def get_room_info(self):
        """获取房间信息"""
        room_info = await live.get_room_info(self.room_id)
        return room_info

    def exists(self):
        return self.find_one(room_id=self.room_id) is not None

    def delete(self):
        return streamer_table.delete(room_id=self.room_id)

    def create(self):
        if self.exists():
            raise ValueError(f"{self.room_id} 已存在")

        return streamer_table.insert(asdict(self))

    def update(self, data):
        streamer_table.update({**data, "room_id": self.room_id}, ["room_id"])


@dataclass
class User:
    """
    需要推送消息的用户
    """

    uid: int  # 用户 ID
