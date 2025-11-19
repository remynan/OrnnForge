import uuid
from datetime import datetime
from typing import Dict, List
import asyncio
import aiohttp
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import config
from src.log import logger
from src.types import CreationItem


async def get_all_routes() -> Dict[str, str]:
    """获取所有可用的路由"""
    url = f'{config.DAILY_HOT_API_BASE_URL}/all'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    code = data.get('code', 500)
    useful_routes = {
        'baidu': None,
        'bilibili': None,
        'douyin': None,
        'douban-group': None,
        'douban-movie': None,
        'hupu': None,
        'sina': None,
        'tieba': None,
        'toutiao': None,
        'qq-news': None,
        'sina-news': None,
        'netease-news': None,
        'thepaper': None,
        'zhihu-daily': None,
    }

    if code == 200:
        routes = data.get('routes', [])
        for route in routes:
            name = route.get('name', '')
            path = route.get('path', None)
            if path and name and name in useful_routes:
                useful_routes[name] = path

    return useful_routes


async def get_top_data_by_path(session: aiohttp.ClientSession, path: str, source: str) -> List[CreationItem]:
    """根据路径获取热门数据"""
    url = f'{config.DAILY_HOT_API_BASE_URL}{path}'
    logger.debug(f'url: {url}')

    try:
        async with session.get(url) as response:
            data = await response.json()

        code = data.get('code', 500)
        result = []

        if code == 200:
            logger.debug(f'data: {data}')
            top_data = data.get('data', [])

            for top in top_data:
                top_id = top.get('id', None)
                if top_id:
                    top['_id'] = uuid.uuid4().hex
                    top.pop('id')
                    top['source'] = source
                    top['create_time'] = datetime.now()
                    top['top_id'] = str(top_id)

                    # 处理时间戳
                    timestamp = top.get('timestamp', None)
                    if isinstance(timestamp, int):
                        timestamp_str = str(timestamp)
                        if len(timestamp_str) == 13:
                            timestamp_s = int(timestamp_str[:10])
                            timestamp_dt = datetime.fromtimestamp(timestamp_s)
                            timestamp_str = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
                        elif len(timestamp_str) == 19:
                            timestamp_str = None
                        else:
                            timestamp_dt = datetime.fromtimestamp(timestamp)
                            timestamp_str = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
                        top['timestamp'] = timestamp_str

                    result.append(CreationItem(**top))

        return result

    except Exception as e:
        logger.error(f"Error fetching data from {url}: {e}")
        return []


async def save_to_mongodb(collection, top_items: List[CreationItem]):
    """将数据保存到 MongoDB"""
    if not top_items:
        return

    try:
        documents = [item.model_dump() for item in top_items]
        result = await collection.insert_many(documents)
        logger.info(f"Successfully inserted {len(result.inserted_ids)} documents into MongoDB")

    except Exception as e:
        logger.error(f"Error saving to MongoDB: {e}")


async def process_single_source(session: aiohttp.ClientSession, collection, source: str, path: str):
    """处理单个数据源"""
    if path is None:
        logger.warning(f"No path found for source: {source}")
        return

    logger.info(f"Processing source: {source}")
    top_data = await get_top_data_by_path(session, path, source)

    if top_data:
        logger.debug(f"Found {len(top_data)} items for {source}")
        await save_to_mongodb(collection, top_data)
    else:
        logger.warning(f"No data found for source: {source}")


async def main():
    """主函数"""

    # 创建 MongoDB 连接
    client = AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.DATABASE_NAME]
    collection = db[config.COLLECTION_NAME]

    try:
        # 获取所有路由
        routes = await get_all_routes()
        logger.debug(f"Available routes: {routes}")

        keys_to_process = list(routes.keys())[:10]
        logger.debug(f"Processing keys: {keys_to_process}")

        async with aiohttp.ClientSession() as session:
            tasks = []
            for key in keys_to_process:
                # 如果只想处理特定源，可以取消下面的注释
                # if key != 'hupu':
                #     continue
                path = routes[key]
                task = process_single_source(session, collection, key, path)
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        # 关闭 MongoDB 连接
        client.close()


async def create_indexes():
    """创建数据库索引（幂等操作）"""
    client = AsyncIOMotorClient(config.MONGODB_URL)
    db = client[config.DATABASE_NAME]
    collection = db[config.COLLECTION_NAME]
    existing_indexes = await collection.list_indexes().to_list(length=None)
    existing_index_names = [index["name"] for index in existing_indexes]

    indexes_to_create = []

    # 检查复合索引是否存在
    if "source_1_top_id_1" not in existing_index_names:
        indexes_to_create.append([("source", 1), ("top_id", 1)])

    # 检查时间索引是否存在
    if "create_time_-1" not in existing_index_names:
        indexes_to_create.append([("create_time", -1)])

    # 检查状态索引是否存在
    if "status_1" not in existing_index_names:
        indexes_to_create.append([("status", 1)])

    # 检查删除标志索引是否存在
    if "del_flag_1" not in existing_index_names:
        indexes_to_create.append([("del_flag", 1)])

    # 创建缺失的索引
    for index_spec in indexes_to_create:
        if len(index_spec) == 2 and isinstance(index_spec[0], tuple):
            # 复合索引
            await collection.create_index(
                index_spec,
                unique=True,
                name=f"{index_spec[0][0]}_{index_spec[0][1]}_{index_spec[1][0]}_{index_spec[1][1]}"
            )
        else:
            # 单字段索引
            field, direction = index_spec[0]
            direction_str = "1" if direction == 1 else "-1"
            await collection.create_index(index_spec, name=f"{field}_{direction_str}")

    if indexes_to_create:
        logger.info(f"Created {len(indexes_to_create)} new indexes")
    else:
        logger.info("All indexes already exist")


if __name__ == '__main__':
    # 创建索引
    asyncio.run(create_indexes())

    # 运行主程序
    asyncio.run(main())