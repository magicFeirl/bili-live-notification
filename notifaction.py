import os
import asyncio

import config
from app.notification import blive

os.environ["HTTP_PROXY"] = os.environ["HTTPS_PROXY"] = config.PROXY

if __name__ == "__main__":
    # run_polling()
    asyncio.run(blive.notification())
