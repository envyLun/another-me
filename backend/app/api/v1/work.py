"""
工作场景 API 路由
提供工作相关的智能辅助功能接口
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.services.work_service import get_work_service, WorkService
from app.core.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()


# ==================== 请求模型 ====================

class WeeklyReportRequest(BaseModel):
    """周报生成请求"""
    start_date: Optional[str] = Field(None, description="开始日期 YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="结束日期 YYYY-MM-DD")


class OrganizeTodosRequest(BaseModel):
    """待办整理请求"""
    todos: List[str] = Field(..., description="原始待办事项列表")


class MeetingSummaryRequest(BaseModel):
    """会议总结请求"""
    meeting_notes: str = Field(..., description="会议记录内容")
    meeting_info: Optional[dict] = Field(None, description="会议信息（标题、时间、参与者等）")


class ProjectProgressRequest(BaseModel):
    """项目进度请求"""
    project_name: str = Field(..., description="项目名称")


# ==================== API 端点 ====================

@router.post("/weekly-report")
async def generate_weekly_report(
    request: WeeklyReportRequest,
    service: WorkService = Depends(get_work_service)
):
    """
    生成工作周报
    
    根据指定时间范围内的工作记录，自动生成周报内容。
    如果不指定日期，则生成上一周的周报。
    """
    logger.info(f"API: Generate weekly report request")
    
    try:
        # 解析日期
        start_date = datetime.fromisoformat(request.start_date) if request.start_date else None
        end_date = datetime.fromisoformat(request.end_date) if request.end_date else None
        
        # 调用服务
        result = await service.generate_weekly_report(
            start_date=start_date,
            end_date=end_date
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to generate weekly report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/organize-todos")
async def organize_todos(
    request: OrganizeTodosRequest,
    service: WorkService = Depends(get_work_service)
):
    """
    智能整理待办事项
    
    对原始待办列表进行智能分类、优先级排序和去重。
    """
    logger.info(f"API: Organize {len(request.todos)} todos")
    
    try:
        result = await service.organize_todos(
            raw_todos=request.todos
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to organize todos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize-meeting")
async def summarize_meeting(
    request: MeetingSummaryRequest,
    service: WorkService = Depends(get_work_service)
):
    """
    总结会议内容
    
    根据会议记录自动生成会议总结，提取关键讨论点、决策事项和行动项。
    """
    logger.info("API: Summarize meeting")
    
    try:
        result = await service.summarize_meeting(
            meeting_notes=request.meeting_notes,
            meeting_info=request.meeting_info
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to summarize meeting: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/track-project")
async def track_project_progress(
    request: ProjectProgressRequest,
    service: WorkService = Depends(get_work_service)
):
    """
    追踪项目进度
    
    分析项目相关的所有工作记录，生成项目进度报告。
    """
    logger.info(f"API: Track project progress: {request.project_name}")
    
    try:
        result = await service.track_project_progress(
            project_name=request.project_name
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to track project progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))
