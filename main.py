import asyncio
from bson import ObjectId
from langchain_openai import ChatOpenAI
from motor.motor_asyncio import AsyncIOMotorClient
from src.config import config
from src.log import logger
from src.templates import hupu
from src.types import FormForCreationGenerate

chat = ChatOpenAI(
    model="glm-4.5-flash",
    base_url='https://open.bigmodel.cn/api/paas/v4'
)


async def generate_by_form(form: FormForCreationGenerate, to_key: str):
    messages = hupu.get_template(to_key).invoke({'html': form.html, 'idea': form.idea})

    response = chat.invoke(messages)
    content = response.content
    return content


async def main():
    try:
        client = AsyncIOMotorClient(config.MONGODB_URL)
        db = client.get_database(config.DATABASE_NAME)
        collection = db.get_collection(config.COLLECTION_NAME)
        logger.info("Connected to MongoDB successfully")

        # 创建索引
        await collection.create_index([("create_time", -1)])
        await collection.create_index([("status", 1)])
        await collection.create_index([("source", 1)])
        await collection.create_index([("del_flag", 1)])
        logger.info("Database indexes created")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise e
    while True:
        item = await collection.find_one(
            {"status": 1, "source": 'hupu', "del_flag": False}
        )
        if not item:
            logger.warning(f"Item not found: {item}")
            await asyncio.sleep(10)
            continue
        object_id = item.get('_id', None)
        form_data = item.get("formForGenerate", {})
        result = item.get("result", {})
        if not form_data or object_id is None:
            logger.warning(f"Item not found: {item}")
            await asyncio.sleep(10)
            continue
        form = FormForCreationGenerate(**form_data)
        logger.info(f"Found One: {object_id}")
        to_keys = ['kuaishou', 'red', 'bilibili', 'douyin']
        updated_result = await collection.update_one(
            {"_id": ObjectId(object_id)},
            {"$set":
                {
                    "status": 2
                }
            }
        )
        if updated_result.modified_count == 0:
            logger.warning(f"更新生成中状态失败")
        else:
            logger.debug(f"Updated status: 生成中")
        for to_key in to_keys:
            logger.debug(f"Generating for {to_key}")
            content = await generate_by_form(form, to_key)
            result[to_key] = content
        updated_result = await collection.update_one(
            {"_id": ObjectId(object_id)},
            {"$set":
                {
                    "status": 3,
                    "result": result
                }
            }
        )
        if updated_result.modified_count == 0:
            logger.error(f"Failed to update {object_id}")
        else:
            logger.debug(f"Updated {object_id}")


if __name__ == '__main__':
    asyncio.run(main())