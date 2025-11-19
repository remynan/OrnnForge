
class Configuration:
    MONGODB_URL: str = "mongodb://admin:dhc1234@172.16.232.155:27017"
    DATABASE_NAME: str = "daily_hot"
    COLLECTION_NAME: str = "creation_items"
    DAILY_HOT_API_BASE_URL: str = 'https://dailyhotapi.3yu3.top'

config = Configuration()