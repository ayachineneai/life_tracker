# Life Tracker 数据结构文档

> `occurred_at`：事件发生时间，用户指定。
> `recorded_at`：写入系统的时间，自动记录，不可修改。

## weight（体重）

| 字段        | 类型 | 必填 | 说明                     |
|-------------|------|------|--------------------------|
| id          | INT  | 自动 | 主键                     |
| weight_kg   | REAL | ✅   | 体重（kg）               |
| occurred_at | TEXT | ✅   | 称重时间（用户指定）     |
| recorded_at | TEXT | 自动 | 记录时间（系统写入）     |

---

## diet（饮食）

| 字段        | 类型 | 必填 | 说明                         |
|-------------|------|------|------------------------------|
| id          | INT  | 自动 | 主键                         |
| calories    | REAL | ✅   | 热量（kcal）                 |
| notes       | TEXT | ❌   | 饮食内容（米饭、鸡胸肉…）    |
| image_path  | TEXT | ❌   | 餐食照片本地路径             |
| occurred_at | TEXT | ✅   | 用餐时间（用户指定）         |
| recorded_at | TEXT | 自动 | 记录时间（系统写入）         |

---

## training_sessions（训练）

| 字段        | 类型 | 必填 | 说明                     |
|-------------|------|------|--------------------------|
| id          | INT  | 自动 | 主键                     |
| title       | TEXT | ✅   | 训练标题（腿日、胸背日…）|
| notes       | TEXT | ❌   | 备注                     |
| started_at  | TEXT | ✅   | 训练开始时间（用户指定） |
| ended_at    | TEXT | ❌   | 训练结束时间（用户指定） |
| recorded_at | TEXT | 自动 | 记录时间（系统写入）     |

## training_exercises（训练动作）

| 字段        | 类型 | 必填 | 说明                                                      |
|-------------|------|------|-----------------------------------------------------------|
| id          | INT  | 自动 | 主键                                                      |
| session_id  | INT  | ✅   | 关联 training_sessions.id                                 |
| exercise    | TEXT | ✅   | 动作名称（深蹲、卧推…）                                  |
| sets        | TEXT | ✅   | 每组数据：`[{"reps": 10, "weight_kg": 80}, …]`           |
| recorded_at | TEXT | 自动 | 记录时间（系统写入）                                     |

---

## cardio（有氧训练）

| 字段         | 类型 | 必填 | 说明                             |
|--------------|------|------|----------------------------------|
| id           | INT  | 自动 | 主键                             |
| type         | TEXT | ✅   | 类型（爬坡、跑步、骑行…）        |
| duration_min | INT  | ✅   | 时长（分钟）                     |
| speed_kmh    | REAL | ❌   | 速度（km/h）                     |
| incline_pct  | REAL | ❌   | 坡度（%）                        |
| distance_km  | REAL | ❌   | 距离（km）                       |
| occurred_at  | TEXT | ✅   | 训练时间（用户指定）             |
| recorded_at  | TEXT | 自动 | 记录时间（系统写入）             |

---

## spending（消费）

| 字段        | 类型 | 必填 | 说明                             |
|-------------|------|------|----------------------------------|
| id          | INT  | 自动 | 主键                             |
| amount      | REAL | ✅   | 金额                             |
| category    | TEXT | ✅   | 类别（餐饮、交通、购物…）        |
| notes       | TEXT | ❌   | 备注                             |
| occurred_at | TEXT | ✅   | 支付时间（用户指定）             |
| recorded_at | TEXT | 自动 | 记录时间（系统写入）             |

---

## piano（练琴）

| 字段          | 类型 | 必填 | 说明                     |
|---------------|------|------|--------------------------|
| id            | INT  | 自动 | 主键                     |
| piece         | TEXT | ✅   | 曲目名称                 |
| duration_min  | INT  | ✅   | 时长（分钟）             |
| measures_from | INT  | ❌   | 练习起始小节             |
| measures_to   | INT  | ❌   | 练习结束小节             |
| occurred_at   | TEXT | ✅   | 练琴时间（用户指定）     |
| recorded_at   | TEXT | 自动 | 记录时间（系统写入）     |
