# 简单的 B 站用户直播推送 Telegram Bot

## 支持功能

1. 添加直播开始/结束推送
2. 移除直播间推送
3. 列出已添加的直播间
4. 支持静音推送

## 开始使用：

**配置文件**

修改 `config.example.py` 为 `config.py` 并填入需要的变量

**main\.py - Bot 监听**

`uv run main.py` 启动 Bot

**notifaction\.py 直播状态轮询**

根据需求添加 cron：
```bash
# 每隔一分钟检查订阅直播间的状态
* * * * * cd <项目路径> && uv run notifaction.py 
```
