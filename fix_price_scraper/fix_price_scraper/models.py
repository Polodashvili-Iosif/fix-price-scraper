from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PriceData(BaseModel):
    current: Optional[float] = None
    original: Optional[float] = None
    sale_tag: Optional[str] = None


class StockData(BaseModel):
    in_stock: Optional[bool] = None
    count: int = 0


class AssetsData(BaseModel):
    main_image: Optional[str] = None
    set_images: List[str] = []
    view360: List[str] = []
    video: List[str] = []


class Product(BaseModel):
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now().timestamp())
    )
    RPC: Optional[str]
    url: str
    title: str
    marketing_tags: List[str] = []
    brand: Optional[str]
    section: List[str]
    price_data: PriceData = Field(default_factory=PriceData)
    stock: StockData = Field(default_factory=StockData)
    assets: AssetsData = Field(default_factory=AssetsData)
    metadata: Dict[str, Optional[str]] = {}
    variants: Optional[int] = None
