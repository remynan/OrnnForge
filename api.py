from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.config import config
from src.log import logger
from src.types import *

# MongoDB
collection: AsyncIOMotorCollection | None = None

@asynccontextmanager
async def lifespan(use_app: FastAPI):
    # Startup
    global collection
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

    yield

    # Shutdown
    if client:
        client.close()
        logger.info("MongoDB connection closed")


# 初始化FastAPI应用
app = FastAPI(lifespan=lifespan)


@app.get("/items", response_model=CreationDataResponse)
async def get_items(
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Page size"),
        status: Optional[int] = Query(0, description="Filter by status"),
        source: Optional[str] = Query(None, description="Filter by source")
):
    """
    获取创建项列表
    - 默认按 create_time 降序排列（从新到旧）
    - 默认只查询未删除的数据 (del_flag=False)
    - 支持按 status 和 source 过滤
    """
    try:
        # 构建查询条件
        query: Dict[str, Any] = {
            "status": status,
            "del_flag": False
        }

        if source:
            query["source"] = source

        # 计算分页
        skip = (page - 1) * size

        # 获取总数
        total = await collection.count_documents(query)
        # 查询数据
        cursor = collection.find(query).sort("create_time", -1).skip(skip).limit(size)
        items = await cursor.to_list(length=size)
        logger.info(f"Found {len(items)} items")
        response_data = CreationData(
            items=items,
            total=total,
            page=page,
            size=size
        )
        return CreationDataResponse(
            code=200,
            message="OK",
            data=response_data
        )

    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/creations/{creation_id}/info", response_model=CreationDataResponse)
async def get_info_by_id(creation_id: str):
    """
    根据ID获取单个创建项
    """
    try:
        item = await collection.find_one({"_id": ObjectId(creation_id), "del_flag": False})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item = dict(item)
        item_result = item.get('result', {})
        format_results = []
        if item_result:
            for k, v in item_result.items():
                format_results.append({
                    "to": k,
                    "content": v
                })
        item['result'] = format_results
        return CreationDataResponse(
            code=200,
            message="OK",
            data=CreationDetailInfo(**item)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {creation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/creations/{creation_id}/generate_form", response_model=CreationDataResponse)
async def get_generate_form_by_id(creation_id: str):
    """
    根据ID获取单个创建项
    """
    try:
        item = await collection.find_one({"_id": ObjectId(creation_id), "del_flag": False})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item = dict(item)
        return CreationDataResponse(
            code=200,
            message="OK",
            data=CreationGenerateForm(**item)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {creation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/creations/generate_form")
async def submit_generate(request: CreationGenerateFormUpdateRequest):
    """
    submit_generate
    """
    try:
        # 转换字符串ID为ObjectId
        object_id = ObjectId(request.id)

        # 执行批量更新
        result = await collection.update_one(
            {"_id": object_id},
            {"$set":
                {
                    "status": 1,
                    "formForGenerate": request.form.model_dump()
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        return {
            "code": 200,
            "message": f"Successfully updated status for {result.modified_count} items"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating items status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")



@app.put("/creations/cannel_generate")
async def cannel_generate(request: OnlyIdRequest):
    """
    根据IDs批量更新status
    """
    try:
        # 转换字符串ID为ObjectId
        object_id = ObjectId(request.id)

        # 执行批量更新
        result = await collection.update_one(
            {"_id": object_id},
            {"$set":
                {
                    "status": 0
                }
            }
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        return {
            "code": 200,
            "message": f"Successfully updated status for {result.modified_count} items"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating items status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.put("/creations/batch_finish")
async def update_items_finish(request: IdsUpdateRequest):
    """
    根据IDs批量更新del_flag（逻辑删除）
    """
    try:
        # 转换字符串ID为ObjectId
        object_ids = [ObjectId(item_id) for item_id in request.ids]

        # 执行批量更新
        result = await collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$set": {"status": 4}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        return {
            'code': 200,
            "message": f"Successfully finished {result.modified_count} items"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating items delete flag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/creations/batch_delete")
async def update_items_delete(request: IdsUpdateRequest):
    """
    根据IDs批量更新del_flag（逻辑删除）
    """
    try:
        # 转换字符串ID为ObjectId
        object_ids = [ObjectId(item_id) for item_id in request.ids]

        # 执行批量更新
        result = await collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$set": {"del_flag": True}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        return {
            'code': 200,
            "message": f"Successfully deleted {result.modified_count} items"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating items delete flag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/items/{item_id}")
async def delete_item_permanently(item_id: str):
    """
    永久删除单个创建项（物理删除）
    """
    try:
        result = await collection.delete_one({"_id": ObjectId(item_id)})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Item not found")

        return {"message": "Item deleted permanently"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)