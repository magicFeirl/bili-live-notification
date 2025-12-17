import re
from string import Template
from datetime import datetime
import httpx


async def get(url, resp_type="json", **kwargs):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
    }

    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url, **kwargs)
        # print(resp.text, resp.request.url)
        if resp_type == "json":
            return resp.json()
        elif resp_type == "text":
            return resp.text
        elif resp_type == "bytes":
            return resp.read()
        else:
            return resp


async def download_assets(url):
    """以 bytes 格式下载资源"""
    return await get(url, resp_type="bytes")


async def get_room_master_info(uid: str):
    """
    获取主播名
    """
    api = "https://api.live.bilibili.com/live_user/v1/Master/info"

    return await get(api, params={"uid": uid})


async def get_room_info(room_id: str):
    """
    获取直播间状态：是否开播、封面、直播时间等
    """
    api = "https://api.live.bilibili.com/room/v1/Room/get_info"

    return await get(api, params={"room_id": room_id})


def format_live_message(room_id: str):
    resp = get_room_info(room_id)

    if resp["code"] != 0:
        return

    room_info = resp["data"]

    uid = room_info.get("uid")
    live_id = str(room_info.get("room_id"))
    title = room_info.get("title")
    user_cover = room_info.get("user_cover")
    live_status = room_info.get("live_status")
    live_time = room_info.get("live_time")
    if live_time[:4] != "0000":
        minutes = (
            datetime.now() - datetime.strptime(live_time, "%Y-%m-%d %H:%M:%S")
        ).total_seconds() / 60
    else:
        minutes = 0

    minutes = round(minutes)

    master_info_resp = get_room_master_info(uid)
    user_info = master_info_resp["data"]["info"]
    username = user_info["uname"]

    message = Template("""
        $title 
        开播时间 $live_time

        $minutes 分钟前
    """).substitute(title=title, live_time=live_time, minutes=minutes)

    message = re.sub(r"\n\s+(.)", r"\n\g<1>", message.strip())
    actions = (
        f"view, 看!, bilibili://live/{live_id}; view, 看(h5)!, https://live.bilibili.com/h5/{live_id}".encode()
        if live_status == 1
        else ""
    )

    return (
        live_status,
        username,
        {
            "message": message.encode(),
            "headers": {
                "Title": f"{username}{'开' if live_status == 1 else '下'}播了".encode(),
                "Attach": user_cover,
                "Tags": "loudspeaker",
                "Actions": actions,
            },
        },
    )
