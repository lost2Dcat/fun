#!/usr/bin/env python3
"""AI 产品内测推广运营日程管理器（CLI）"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DATETIME_FMT = "%Y-%m-%d %H:%M"
DEFAULT_DB = Path("beta_schedule.json")


@dataclass
class Task:
    id: int
    title: str
    owner: str
    channel: str
    start_at: str
    end_at: str
    priority: str
    status: str
    goal: str
    notes: str

    def matches_keyword(self, keyword: Optional[str]) -> bool:
        if not keyword:
            return True
        haystack = " ".join([self.title, self.owner, self.channel, self.goal, self.notes]).lower()
        return keyword.lower() in haystack


class ScheduleManager:
    def __init__(self, db_path: Path = DEFAULT_DB) -> None:
        self.db_path = db_path
        self.tasks = self._load()

    def _load(self) -> List[Task]:
        if not self.db_path.exists():
            return []
        payload = json.loads(self.db_path.read_text(encoding="utf-8"))
        return [Task(**item) for item in payload.get("tasks", [])]

    def _save(self) -> None:
        data = {"tasks": [asdict(t) for t in self.tasks]}
        self.db_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def _next_id(self) -> int:
        if not self.tasks:
            return 1
        return max(task.id for task in self.tasks) + 1

    @staticmethod
    def _validate_time(dt_str: str) -> None:
        datetime.strptime(dt_str, DATETIME_FMT)

    def add_task(self, **kwargs: Any) -> Task:
        self._validate_time(kwargs["start_at"])
        self._validate_time(kwargs["end_at"])
        task = Task(id=self._next_id(), **kwargs)
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.start_at)
        self._save()
        return task

    def list_tasks(self, status: Optional[str] = None, owner: Optional[str] = None, keyword: Optional[str] = None) -> List[Task]:
        results = self.tasks
        if status:
            results = [t for t in results if t.status == status]
        if owner:
            results = [t for t in results if t.owner == owner]
        if keyword:
            results = [t for t in results if t.matches_keyword(keyword)]
        return sorted(results, key=lambda t: t.start_at)

    def update_status(self, task_id: int, status: str) -> Task:
        task = self._find(task_id)
        task.status = status
        self._save()
        return task

    def remove_task(self, task_id: int) -> Task:
        task = self._find(task_id)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._save()
        return task

    def dashboard(self) -> Dict[str, Any]:
        by_status: Dict[str, int] = {}
        by_channel: Dict[str, int] = {}
        owners: Dict[str, int] = {}

        for task in self.tasks:
            by_status[task.status] = by_status.get(task.status, 0) + 1
            by_channel[task.channel] = by_channel.get(task.channel, 0) + 1
            owners[task.owner] = owners.get(task.owner, 0) + 1

        nearest = sorted(self.tasks, key=lambda t: t.start_at)[:5]
        return {
            "total": len(self.tasks),
            "by_status": by_status,
            "by_channel": by_channel,
            "top_owners": sorted(owners.items(), key=lambda x: x[1], reverse=True),
            "nearest": nearest,
        }

    def seed_template(self) -> None:
        if self.tasks:
            return
        self.add_task(
            title="招募种子用户：官网与社群联动",
            owner="运营-Amy",
            channel="官网+微信群",
            start_at="2026-03-01 10:00",
            end_at="2026-03-03 18:00",
            priority="高",
            status="待开始",
            goal="收集300名符合画像的内测用户",
            notes="官网表单 + 群内问卷双通道，按角色标签筛选",
        )
        self.add_task(
            title="KOC 首轮试用反馈直播",
            owner="市场-Luke",
            channel="视频号直播",
            start_at="2026-03-05 20:00",
            end_at="2026-03-05 21:30",
            priority="中",
            status="待开始",
            goal="沉淀30条可用于二次传播的真实案例",
            notes="直播后48小时剪辑精华，投放朋友圈素材",
        )

    def _find(self, task_id: int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        raise ValueError(f"未找到任务ID: {task_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI 产品内测推广运营日程管理器")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB, help="存储文件路径，默认 beta_schedule.json")

    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="新增任务")
    add.add_argument("--title", required=True)
    add.add_argument("--owner", required=True)
    add.add_argument("--channel", required=True)
    add.add_argument("--start-at", required=True, help=f"格式：{DATETIME_FMT}")
    add.add_argument("--end-at", required=True, help=f"格式：{DATETIME_FMT}")
    add.add_argument("--priority", default="中", choices=["高", "中", "低"])
    add.add_argument("--status", default="待开始", choices=["待开始", "进行中", "已完成", "已取消"])
    add.add_argument("--goal", default="")
    add.add_argument("--notes", default="")

    ls_cmd = sub.add_parser("list", help="查看任务")
    ls_cmd.add_argument("--status")
    ls_cmd.add_argument("--owner")
    ls_cmd.add_argument("--keyword")

    upd = sub.add_parser("update", help="更新状态")
    upd.add_argument("--id", type=int, required=True)
    upd.add_argument("--status", required=True, choices=["待开始", "进行中", "已完成", "已取消"])

    rm = sub.add_parser("remove", help="删除任务")
    rm.add_argument("--id", type=int, required=True)

    sub.add_parser("dashboard", help="查看统计仪表盘")
    sub.add_parser("seed", help="初始化内测推广模板")

    return parser


def print_task(task: Task) -> None:
    print(
        f"[{task.id}] {task.title}\n"
        f"  负责人: {task.owner} | 渠道: {task.channel} | 优先级: {task.priority} | 状态: {task.status}\n"
        f"  时间: {task.start_at} -> {task.end_at}\n"
        f"  目标: {task.goal}\n"
        f"  备注: {task.notes}\n"
    )


def run(args: argparse.Namespace) -> None:
    manager = ScheduleManager(args.db)

    if args.command == "add":
        task = manager.add_task(
            title=args.title,
            owner=args.owner,
            channel=args.channel,
            start_at=args.start_at,
            end_at=args.end_at,
            priority=args.priority,
            status=args.status,
            goal=args.goal,
            notes=args.notes,
        )
        print(f"✅ 已新增任务 #{task.id}: {task.title}")
    elif args.command == "list":
        tasks = manager.list_tasks(status=args.status, owner=args.owner, keyword=args.keyword)
        if not tasks:
            print("暂无匹配任务。")
            return
        for task in tasks:
            print_task(task)
    elif args.command == "update":
        task = manager.update_status(args.id, args.status)
        print(f"✅ 任务 #{task.id} 状态已更新为：{task.status}")
    elif args.command == "remove":
        task = manager.remove_task(args.id)
        print(f"✅ 已删除任务 #{task.id}: {task.title}")
    elif args.command == "dashboard":
        data = manager.dashboard()
        print(f"任务总数: {data['total']}")
        print("按状态统计:", data["by_status"])
        print("按渠道统计:", data["by_channel"])
        print("负责人任务量:", data["top_owners"])
        print("最近日程:")
        for task in data["nearest"]:
            print(f"  - ({task.start_at}) #{task.id} {task.title} [{task.status}]")
    elif args.command == "seed":
        manager.seed_template()
        print("✅ 已初始化内测推广模板（若已有任务则跳过）。")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
