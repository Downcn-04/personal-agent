"""
健康检查 API 路由

提供服务健康检查接口，用于监控和负载均衡。
"""

from datetime import datetime

from fastapi import APIRouter

from app.core import get_settings
from app.models.schemas import HealthCheckResponse

# 创建路由器
router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查服务是否正常运行"
)
async def health_check() -> HealthCheckResponse:
    """健康检查接口
    
    用于监控系统和负载均衡器检查服务状态。
    
    Returns:
        HealthCheckResponse: 健康检查响应
        
    Example:
        ```bash
        curl http://localhost:8000/health
        ```
        
        Response:
        ```json
        {
            "status": "healthy",
            "version": "0.1.0",
            "timestamp": "2026-05-19T10:30:00Z"
        }
        ```
    """
    settings = get_settings()
    
    return HealthCheckResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat() + "Z"
    )
