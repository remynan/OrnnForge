from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from src.config import config
from src.log import logger


# MongoDB
collection: AsyncIOMotorCollection | None = None


class ItemResponse(BaseModel):
    id: str = Field(..., alias="_id")
    source: str
    top_id: str
    title: str
    cover: Optional[str] = None
    desc: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[str] = None
    hot: Optional[int] = None
    url: Optional[str] = None
    mobileUrl: Optional[str] = None
    create_time: str
    status: Optional[str] = "active"
    del_flag: Optional[int] = 0

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}


class ItemsResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    size: int


class StatusUpdateRequest(BaseModel):
    ids: List[str]
    status: str


class DeleteFlagUpdateRequest(BaseModel):
    ids: List[str]
    del_flag: int = Field(..., ge=0, le=1, description="0: active, 1: deleted")


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


@app.get("/items", response_model=ItemsResponse)
async def get_items(
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(20, ge=1, le=100, description="Page size"),
        status: Optional[str] = Query(None, description="Filter by status"),
        source: Optional[str] = Query(None, description="Filter by source")
):
    """
    获取创建项列表
    - 默认按 create_time 降序排列（从新到旧）
    - 默认只查询未删除的数据 (del_flag=0)
    - 支持按 status 和 source 过滤
    """
    try:
        # 构建查询条件
        query: Dict[str, Any] = {"del_flag": 0}

        if status:
            query["status"] = status

        if source:
            query["source"] = source

        # 计算分页
        skip = (page - 1) * size

        # 获取总数
        total = await collection.count_documents(query)

        # 查询数据
        cursor = collection.find(query).sort("create_time", -1).skip(skip).limit(size)
        items = await cursor.to_list(length=size)

        # 转换 ObjectId 为字符串
        for item in items:
            item["_id"] = str(item["_id"])

        return ItemsResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    except Exception as e:
        logger.error(f"Error fetching items: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: str):
    """
    根据ID获取单个创建项
    """
    try:
        item = await collection.find_one({"_id": ObjectId(item_id), "del_flag": 0})

        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        item = dict(item)
        item["_id"] = str(item["_id"])
        return item

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/items/status")
async def update_items_status(request: StatusUpdateRequest):
    """
    根据IDs批量更新status
    """
    try:
        # 转换字符串ID为ObjectId
        object_ids = [ObjectId(item_id) for item_id in request.ids]

        # 执行批量更新
        result = await collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$set": {"status": request.status}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        return {
            "message": f"Successfully updated status for {result.modified_count} items",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating items status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/items/delete-flag")
async def update_items_delete_flag(request: DeleteFlagUpdateRequest):
    """
    根据IDs批量更新del_flag（逻辑删除）
    """
    try:
        # 转换字符串ID为ObjectId
        object_ids = [ObjectId(item_id) for item_id in request.ids]

        # 执行批量更新
        result = await collection.update_many(
            {"_id": {"$in": object_ids}},
            {"$set": {"del_flag": request.del_flag}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="No items found to update")

        action = "deleted" if request.del_flag == 1 else "restored"
        return {
            "message": f"Successfully {action} {result.modified_count} items",
            "matched_count": result.matched_count,
            "modified_count": result.modified_count
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