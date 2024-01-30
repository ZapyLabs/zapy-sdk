import magicattr
from fastapi import APIRouter

from zapy.store.attr import Attr, build_attr_info
from zapy.store.context import Stores

api_store_v1 = APIRouter(tags=["v1"])


@api_store_v1.get("/stores/{store_id}")
async def get_store(store_id: str) -> Attr:
    stores = Stores()
    attr = magicattr.get(stores, store_id)
    return build_attr_info(attr, store_id)
