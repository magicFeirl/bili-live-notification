import os

from app.telegram.bot import run_polling
import config

os.environ["HTTP_PROXY"] = os.environ["HTTPS_PROXY"] = config.PROXY

if __name__ == "__main__":
    run_polling()
