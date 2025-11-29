from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, List
from datetime import datetime

class ProductItem(BaseModel):
    # ========== 必采字段 ==========
    # 商品基础信息
    product_id: Optional[str] = Field(None, description="Jumia内部商品唯一ID (data-gtm-id)")
    name: str = Field(..., description="商品名称")
    brand: Optional[str] = Field(None, description="品牌 (data-gtm-brand)")
    url: str = Field(..., description="商品详情页链接")
    image_url: Optional[str] = Field(None, description="主图链接")
    
    # 价格信息
    currency: str = Field(..., description="货币符号, e.g. NGN, KSh")
    current_price: float = Field(..., description="当前售价/现价")
    
    # 评价信息
    rating: Optional[float] = Field(None, description="评分 (0-5)")
    review_count: Optional[int] = Field(0, description="评论数/评论量")
    
    # 类目与卖家
    seller_id: Optional[str] = Field(None, description="店铺ID/Seller ID (data-gtm-dimension23)")
    category_path: Optional[List[str]] = Field(default_factory=list, description="完整类目层级 (data-gtm-category)")
    
    # ========== 建议采集字段 ==========
    old_price: Optional[float] = Field(None, description="原价/划线价")
    discount_percentage: Optional[float] = Field(None, description="折扣百分比")
    promo_tag: Optional[str] = Field(None, description="促销活动标签 (e.g. Black Friday deal)")
    is_express: bool = Field(False, description="是否为Jumia Express (Prime-like)")
    gtm_tags: Optional[List[str]] = Field(default_factory=list, description="Jumia内部标签集 (data-gtm-dimension43)")
    list_position: Optional[int] = Field(None, description="商品在列表页的排序位置")
    
    # ========== 可选字段 ==========
    rating_ratio: Optional[float] = Field(None, description="评分比例 (用于校验, 0-1)")
    ga4_category_1: Optional[str] = Field(None, description="GA4一级类目")
    ga4_category_2: Optional[str] = Field(None, description="GA4二级类目")
    ga4_price: Optional[float] = Field(None, description="GA4价格 (可能为美元或内部计价)")
    is_second_chance: Optional[bool] = Field(None, description="是否为二次曝光 (data-ga4-is_second_chance)")
    
    # ========== 原有字段 (保留兼容性) ==========
    sku: Optional[str] = Field(None, description="商品唯一标识 (备用)")
    is_shipped_from_abroad: bool = Field(False, description="是否海外发货")
    crawled_at: datetime = Field(default_factory=datetime.utcnow, description="采集时间")

    @field_validator('url', 'image_url', mode='before')
    def validate_url(cls, v):
        if v and not v.startswith('http'):
            # Handle relative URLs if necessary, though scraper should handle this
            pass
        return v
    
    @field_validator('category_path', 'gtm_tags', mode='before')
    def validate_list_fields(cls, v):
        """处理列表字段,确保返回列表类型"""
        if v is None:
            return []
        if isinstance(v, str):
            # 如果是字符串,尝试分割
            if '|' in v:
                return [x.strip() for x in v.split('|') if x.strip()]
            elif ' / ' in v:
                return [x.strip() for x in v.split(' / ') if x.strip()]
            return [v] if v else []
        return v if isinstance(v, list) else []
