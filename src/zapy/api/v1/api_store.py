import magicattr

from zapy.store.context import Stores
from zapy.store.attr import build_attr_info, Attr

from fastapi import APIRouter


api_store_v1 = APIRouter(tags=["v1"])


@api_store_v1.get("/stores/{store_id}")
async def get_store(store_id: str) -> Attr:
    stores = Stores()
    attr = magicattr.get(stores, store_id)
    return build_attr_info(attr, store_id)

