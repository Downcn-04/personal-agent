"""
数据转换工具

提供 ORM 模型与 DTO 之间的转换函数。
"""

from datetime import datetime
from typing import Any, TypeVar

from pydantic import BaseModel

# 泛型类型变量
T = TypeVar("T", bound=BaseModel)


def convert_datetime_to_str(dt: datetime) -> str:
    """将 datetime 对象转换为 ISO 格式字符串
    
    Args:
        dt: datetime 对象
        
    Returns:
        str: ISO 格式字符串（例如：2026-05-19T10:30:00）
        
    Example:
        ```python
        from datetime import datetime
        
        dt = datetime.now()
        iso_str = convert_datetime_to_str(dt)
        print(iso_str)  # "2026-05-19T10:30:00"
        ```
    """
    return dt.isoformat()


def convert_orm_to_dto(orm_obj: Any, dto_class: type[T]) -> T:
    """将 ORM 模型对象转换为 DTO 对象
    
    自动处理字段映射和类型转换。
    
    Args:
        orm_obj: ORM 模型对象
        dto_class: 目标 DTO 类
        
    Returns:
        T: DTO 对象实例
        
    Example:
        ```python
        from app.models import Thread
        from app.models.schemas import ThreadOut
        
        thread = Thread(id="123", title="Test", created_at=datetime.now())
        thread_out = convert_orm_to_dto(thread, ThreadOut)
        ```
    """
    # 获取 DTO 类的字段
    dto_fields = dto_class.model_fields.keys()
    
    # 构建字段字典
    data = {}
    for field in dto_fields:
        if hasattr(orm_obj, field):
            value = getattr(orm_obj, field)
            
            # 特殊处理 datetime 类型
            if isinstance(value, datetime):
                data[field] = convert_datetime_to_str(value)
            else:
                data[field] = value
    
    # 创建 DTO 实例
    return dto_class(**data)
