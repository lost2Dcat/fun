# AI 产品内测推广运营日程管理器（小白版）

你可以把它理解成一个**命令行待办工具**，专门用来管理 AI 产品内测期间的运营排期。

---

## 先说结论：你只要执行这 3 步

在项目目录里执行：

```bash
./quick_start.sh
```

这个脚本会自动帮你：
1. 检查 Python 是否安装
2. 初始化示例任务
3. 打印任务列表和仪表盘

> 如果提示没有执行权限，先运行：
>
> ```bash
> chmod +x quick_start.sh
> ./quick_start.sh
> ```

---

## 手动运行（一步一步）

### 第 0 步：确认你在项目目录

```bash
pwd
```

看到路径里有这个项目即可（比如 `/workspace/fun`）。

### 第 1 步：确认 Python

```bash
python3 --version
```

建议 `3.9+`。

### 第 2 步：初始化示例数据

```bash
python3 scheduler.py seed
```

执行后会生成一个数据文件：`beta_schedule.json`。

### 第 3 步：查看任务

```bash
python3 scheduler.py list
```

### 第 4 步：查看总览仪表盘

```bash
python3 scheduler.py dashboard
```

---

## 你最常用的 4 个命令

### 1) 新增任务

```bash
python3 scheduler.py add \
  --title "知乎种草内容首发" \
  --owner "内容-Mia" \
  --channel "知乎" \
  --start-at "2026-03-08 09:30" \
  --end-at "2026-03-08 18:00" \
  --priority "高" \
  --status "待开始" \
  --goal "完成3篇场景化测评帖并引导预约" \
  --notes "设置产品经理答疑楼中楼"
```

### 2) 查任务（支持筛选）

```bash
python3 scheduler.py list
python3 scheduler.py list --status "进行中"
python3 scheduler.py list --owner "运营-Amy"
python3 scheduler.py list --keyword "直播"
```

### 3) 更新状态

```bash
python3 scheduler.py update --id 2 --status "进行中"
```

### 4) 删除任务

```bash
python3 scheduler.py remove --id 2
```

---

## 常见报错（新手必看）

### 报错：`python3: command not found`
说明电脑里还没装 Python 3。

### 报错：`time data ... does not match format '%Y-%m-%d %H:%M'`
时间格式写错了，必须是这种格式：`2026-03-08 09:30`。

### 报错：`未找到任务ID`
说明你更新/删除时输入的 `--id` 不存在，先 `list` 看一下真实 ID。

---

## 进阶：多份计划文件

如果你想给不同团队分开管理，可以用 `--db`：

```bash
python3 scheduler.py --db team_a.json seed
python3 scheduler.py --db team_a.json list
```
