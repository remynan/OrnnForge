import os
from pathlib import Path
from dotenv import load_dotenv


# 加载 .env 文件 为环境变量
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

class Configuration:

    MONGODB_URL: str = os.getenv('MONGODB_URL')
    DATABASE_NAME: str = os.getenv('DATABASE_NAME')
    COLLECTION_NAME: str = os.getenv('COLLECTION_NAME')
    DAILY_HOT_API_BASE_URL: str = os.getenv('DAILY_HOT_API_BASE_URL')

config = Configuration()