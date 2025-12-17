机器人需要的指令：
* /add 添加直播间
* /rm  移除直播间
* /ls  列出监听的直播间
* /slient 设置某直播开播不提醒

数据库字段：
主播信息：
status: 0 or 1 是否开播中
live_start: 开播时间
live_end: 下播时间
is_delete: 是否被标记删除
cover_url: 封面 URL
uid:  主播ID
name: 主播名
title: 直播标题
slient: 0 or 1 是否静音推送

推送用户：指定机器人能给哪些用户推送消息
uid: 用户 ID

管理用户：指定可以操作机器人指令的用户
uid: 用户 ID 