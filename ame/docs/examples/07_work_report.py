"""
示例 7: 工作报告生成

演示如何使用 Work Services 生成各类工作报告。
"""

import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Any

from ame.foundation.llm import OpenAICaller
from ame.foundation.embedding import OpenAIEmbedding
from ame.foundation.storage import VectorStore, GraphStore, DocumentStore
from ame.capabilities import CapabilityFactory
from ame.services.work import ReportService, TodoService, MeetingService, ProjectService


async def demo_weekly_report(service: ReportService):
    """演示周报生成"""
    print("\n" + "=" * 60)
    print("周报生成演示")
    print("=" * 60)
    
    # 生成周报
    print("\n[1] 生成本周工作报告...")
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    report = await service.generate_weekly_report(
        user_id="demo_user",
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\n📊 报告期间: {report['period']}")
    print(f"\n💡 关键洞察:")
    for i, insight in enumerate(report.get('insights', []), 1):
        print(f"  {i}. {insight}")
    
    print(f"\n📈 数据统计:")
    stats = report.get('statistics', {})
    print(f"  - 总事件数: {stats.get('total_events', 0)}")
    print(f"  - 工作时长: {stats.get('work_hours', 0)} 小时")
    print(f"  - 完成任务: {stats.get('completed_tasks', 0)} 个")
    
    print(f"\n📝 完整报告:")
    print("-" * 60)
    print(report.get('formatted_report', ''))
    print("-" * 60)


async def demo_todo_management(service: TodoService):
    """演示待办事项管理"""
    print("\n" + "=" * 60)
    print("待办事项管理演示")
    print("=" * 60)
    
    # 测试不同的任务输入
    test_inputs = [
        "明天下午3点前完成项目方案，优先级高",
        "本周五之前准备会议资料",
        "提醒我下周一发送邮件给客户"
    ]
    
    print("\n[1] 智能解析任务...")
    
    for user_input in test_inputs:
        print(f"\n👤 用户输入: {user_input}")
        
        task = await service.parse_task(user_input)
        
        print(f"📋 解析结果:")
        print(f"  - 标题: {task.get('title', 'N/A')}")
        print(f"  - 截止日期: {task.get('deadline', 'N/A')}")
        print(f"  - 优先级: {task.get('priority', 'medium')}")
        print(f"  - 描述: {task.get('description', 'N/A')}")


async def demo_meeting_summary(service: MeetingService):
    """演示会议纪要生成"""
    print("\n" + "=" * 60)
    print("会议纪要生成演示")
    print("=" * 60)
    
    # 模拟会议记录
    meeting_content = """
    今天召开了产品设计评审会议。
    
    讨论内容：
    1. 新版本的UI设计方案
    2. 功能优先级排序
    3. 技术实现方案
    
    张三提出了移动端适配的建议，大家一致同意采纳。
    李四负责完成详细的技术文档，需要在本周五前完成。
    王五需要准备下周的用户测试计划。
    
    最终决定：
    - 采用响应式设计方案
    - 优先开发核心功能
    - 下周一开始技术开发
    """
    
    print("\n[1] 处理会议记录...")
    
    minutes = await service.summarize(
        meeting_content=meeting_content,
        meeting_date=datetime.now(),
        participants=["张三", "李四", "王五", "主持人"]
    )
    
    print(f"\n📝 会议纪要:")
    print("-" * 60)
    print(minutes.get('formatted_minutes', ''))
    print("-" * 60)
    
    print(f"\n🎯 行动项:")
    for item in minutes.get('action_items', []):
        print(f"  - {item['task']} (负责人: {item['owner']}, 截止: {item['deadline']})")


async def demo_project_tracking(service: ProjectService):
    """演示项目进度追踪"""
    print("\n" + "=" * 60)
    print("项目进度追踪演示")
    print("=" * 60)
    
    print("\n[1] 追踪项目进度...")
    
    progress = await service.track_progress(
        project_name="新产品开发",
        user_id="demo_user"
    )
    
    print(f"\n📊 项目: {progress.project_name}")
    print(f"📈 完成率: {progress.completion_rate * 100:.1f}%")
    
    print(f"\n📋 状态统计:")
    status = progress.status
    print(f"  - 总任务数: {status.get('total_tasks', 0)}")
    print(f"  - 已完成: {status.get('completed', 0)}")
    print(f"  - 进行中: {status.get('in_progress', 0)}")
    
    if progress.risks:
        print(f"\n⚠️ 风险提示:")
        for risk in progress.risks:
            print(f"  - {risk}")
    
    print(f"\n📝 进度报告:")
    print("-" * 60)
    print(progress.report)
    print("-" * 60)


async def demo_comprehensive_workflow(
    report_service: ReportService,
    todo_service: TodoService,
    meeting_service: MeetingService,
    project_service: ProjectService
):
    """演示综合工作流"""
    print("\n" + "=" * 60)
    print("综合工作流演示")
    print("=" * 60)
    
    print("\n[场景] 周一早上的工作流程")
    
    # Step 1: 查看上周工作报告
    print("\n📊 Step 1: 查看上周工作报告...")
    weekly_report = await report_service.generate_weekly_report(
        user_id="demo_user",
        start_date=datetime.now() - timedelta(days=7),
        end_date=datetime.now()
    )
    print(f"  ✅ 上周完成 {weekly_report['statistics'].get('completed_tasks', 0)} 个任务")
    
    # Step 2: 处理会议纪要
    print("\n📝 Step 2: 整理周一晨会纪要...")
    minutes = await meeting_service.summarize(
        meeting_content="讨论了本周重点任务...",
        meeting_date=datetime.now()
    )
    print(f"  ✅ 提取了 {len(minutes.get('action_items', []))} 个行动项")
    
    # Step 3: 创建本周任务
    print("\n📋 Step 3: 创建本周任务...")
    tasks = [
        "周三前完成设计评审",
        "周五提交技术方案"
    ]
    for task_input in tasks:
        task = await todo_service.parse_task(task_input)
        print(f"  ✅ 已创建任务: {task['title']}")
    
    # Step 4: 检查项目进度
    print("\n📈 Step 4: 检查项目进度...")
    progress = await project_service.track_progress(
        project_name="新产品开发",
        user_id="demo_user"
    )
    print(f"  ✅ 项目完成率: {progress.completion_rate * 100:.1f}%")
    
    print("\n🎉 本周工作流程规划完成！")


async def main():
    """主函数"""
    print("=" * 60)
    print("AME 工作报告生成示例")
    print("=" * 60)
    
    # 初始化
    print("\n初始化服务...")
    
    llm = OpenAICaller(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    embedding = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY", "sk-..."))
    vector_store = VectorStore(path="./data/vectors")
    graph_store = GraphStore(host="localhost", port=6379)
    document_store = DocumentStore(path="./data/documents")
    
    factory = CapabilityFactory(
        llm_caller=llm,
        embedding_function=embedding,
        vector_store=vector_store,
        graph_store=graph_store,
        document_store=document_store
    )
    
    # 创建各种工作服务
    report_service = ReportService(capability_factory=factory)
    todo_service = TodoService(capability_factory=factory)
    meeting_service = MeetingService(capability_factory=factory)
    project_service = ProjectService(capability_factory=factory)
    
    print("✅ 所有工作服务已初始化")
    
    # 运行演示
    await demo_weekly_report(report_service)
    await demo_todo_management(todo_service)
    await demo_meeting_summary(meeting_service)
    await demo_project_tracking(project_service)
    await demo_comprehensive_workflow(
        report_service,
        todo_service,
        meeting_service,
        project_service
    )
    
    # 总结
    print("\n" + "=" * 60)
    print("✨ 工作报告生成演示完成！")
    print("=" * 60)
    print("\n📖 Work Services 功能:")
    print("  1. ReportService - 周报/月报生成")
    print("  2. TodoService - 智能待办管理")
    print("  3. MeetingService - 会议纪要提取")
    print("  4. ProjectService - 项目进度追踪")
    print("\n💡 这些服务可以组合使用，构建完整的工作管理系统")


if __name__ == "__main__":
    asyncio.run(main())
