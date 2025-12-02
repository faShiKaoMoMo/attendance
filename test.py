import sqlite3
from datetime import datetime

# 1. 连接数据库（没有的话会自动创建）
conn = sqlite3.connect("attendance.db")  # 换成你的数据库文件名
cursor = conn.cursor()

# 课表
cursor.execute('DROP TABLE IF EXISTS "class";')

cursor.execute("""
CREATE TABLE "class" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    start_date DATE,
    end_date DATE,
    create_date TIMESTAMP,
    update_date TIMESTAMP
);
""")

data = """
{
    "0":[
        {"time":["8:00","9:40"],"names":[["吴清强","all"],["刘国前","all"],["向泽旭","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"],["龚星月","all"]]},
        {"time":["10:10","11:50"],"names":[["吴清强","all"],["刘成杨","all"],["刘国前","all"],["向泽旭","even"],["吴滢洁","all"],["黄宇鹏","all"],["林哲帆","all"],["赵婉茹","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
        {"time":["14:30","16:10"],"names":[["刘成杨","odd"],["向泽旭","odd"],["吴滢洁","odd"],["赵婉茹","odd"],["范远生","all"],["王黎明","even"],["陈思涵","even"],["马可心","even"]]},
        {"time":["16:40","18:20"],"names":[["刘国前","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"],["邓椅文","odd"]]},
        {"time":["19:10","20:50"],"names":[["范远生","all"]]}
    ],
    "1":[
        {"time":["8:00","9:40"],"names":[["吴清强","odd"],["刘成杨","all"],["赵婉茹","all"],["刘国英","all"]]},
        {"time":["10:10","11:50"],"names":[["吴清强","odd"],["王美红","all"]]},
        {"time":["14:30","16:10"],"names":[["刘国前","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
        {"time":["16:40","18:20"],"names":[["刘成杨","all"],["刘国前","all"],["向泽旭","all"],["吴滢洁","all"],["柯念昕","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
        {"time":["19:10","20:50"],"names":[["马可心","all"]]}
    ],
    "2":[
        {"time":["8:00","9:40"],"names":[["刘国前","all"],["黄宇鹏","even"],["林哲帆","even"],["赵婉茹","all"],["刘艳","all"],["陈思涵","all"]]},
        {"time":["10:10","11:50"],"names":[["刘成杨","all"],["刘国前","all"],["向泽旭","all"],["吴滢洁","all"],["赵婉茹","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["谢一帆","all"],["龚星月","all"]]},
        {"time":["14:30","16:10"],"names":[["赵婉茹","all"],["王黎明","all"],["马可心","all"],["谢一帆","all"]]},
        {"time":["16:40","18:20"],"names":[["刘成杨","odd"],["向泽旭","odd"],["吴滢洁","odd"],["赵婉茹","odd"],["王黎明","odd"],["马可心","odd"],["谢一帆","all"],["龚星月","all"]]},
        {"time":["19:10","20:50"],"names":[["刘国前","odd"],["吴滢洁","all"],["聂鹏远","all"]]}
    ],
    "3":[
        {"time":["8:00","9:40"],"names":[]},
        {"time":["10:10","11:50"],"names":[["马可心","all"],["龚星月","odd"]]},
        {"time":["14:30","16:10"],"names":[["梁楠","all"]]},
        {"time":["16:40","18:20"],"names":[["刘成杨","even"],["向泽旭","all"],["吴滢洁","even"],["赵婉茹","even"],["范远生","even"],["谢一帆","all"],["刘国英","all"],["龚星月","even"]]},
        {"time":["19:10","20:50"],"names":[["刘成杨","all"],["向泽旭","all"],["吴滢洁","all"],["赵婉茹","all"],["范远生","all"],["刘艳","all"],["谢一帆","all"],["刘国英","all"],["龚星月","all"]]}
    ],
    "4":[
        {"time":["8:00","9:40"],"names":[["林哲帆","odd"],["胡书豪","even"],["杨雨辰","odd"]]},
        {"time":["10:10","11:50"],"names":[["王美红","odd"],["吴滢洁","all"],["范远生","all"],["黄宇鹏","odd"],["谢一帆","all"],["刘国英","all"]]},
        {"time":["14:30","16:10"],"names":[["范远生","all"],["谢一帆","all"]]},
        {"time":["16:40","18:20"],"names":[["刘国英","all"],["龚星月","all"]]},
        {"time":["19:10","20:50"],"names":[["向泽旭","all"],["范远生","all"],["谢一帆","all"],["龚星月","all"]]}
    ]
}
"""

cursor.execute("""
    INSERT INTO class (content, start_date, end_date, create_date, update_date)
    VALUES (?, ?, ?, ?, ?)
""", (
    data,
    "2025-09-01",
    "2025-12-28",
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%Y-%m-%d")
))



# 调课表
cursor.execute('DROP TABLE IF EXISTS "travel";')



# 出差表
cursor.execute('DROP TABLE IF EXISTS "travel";')

cursor.execute("""
CREATE TABLE "travel" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    destination TEXT,
    reason TEXT,
    start_date DATE,
    end_date DATE,
    status INTEGER,
    avg_working_hours DECIMAL,
    description TEXT,
    create_date TIMESTAMP,
    update_date TIMESTAMP
);
""")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_travel_start_date ON travel(start_date)")

test_travel_data = [
    ('王文凯', '九牧', '九牧RPA', '2025-10-27', '2025-11-12', 1, 8, '九牧RPA', '2025-10-27 09:30:00', '2025-10-27T14:20:00'),
    # 新增数据 (状态随机为 0, 1, 2)
    ('李明华', '海尔', '海尔智能家居', '2025-09-15', '2025-09-20', 1, 5, '海尔智能家居', '2025-09-15 10:00:00', '2025-09-15T15:30:00'),  # 审批中
    ('张小雨', '美的', '美的空调项目', '2025-08-01', '2025-08-10', 0, 10, '美的空调项目', '2025-08-01 08:30:00', '2025-08-01T12:00:00'), # 待提交/草稿
    ('陈伟', '格力', '格力工业设计', '2025-10-05', '2025-10-09', 2, 4, '格力工业设计', '2025-10-05 14:00:00', '2025-10-05T18:50:00'),  # 完成
    ('刘芳', '小米', '小米AIoT平台', '2025-07-20', '2025-07-25', 1, 6, '小米AIoT平台', '2025-07-20 07:45:00', '2025-07-20T11:00:00'),  # 审批中
    ('赵刚', '华为', '华为云服务', '2025-09-28', '2025-10-04', 2, 7, '华为云服务', '2025-09-28 11:20:00', '2025-09-28T16:10:00'),  # 完成
    ('杨丽', '阿里巴巴', '阿里钉钉集成', '2025-06-10', '2025-06-18', 0, 9, '阿里钉钉集成', '2025-06-10 09:00:00', '2025-06-10T13:40:00'),  # 待提交/草稿
    ('周杰', '腾讯', '腾讯微信支付', '2025-10-15', '2025-10-22', 1, 8, '腾讯微信支付', '2025-10-15 13:00:00', '2025-10-15T17:25:00'),  # 审批中
    ('吴敏', '百度', '百度自动驾驶', '2025-08-25', '2025-09-03', 2, 10, '百度自动驾驶', '2025-08-25 06:30:00', '2025-08-25T10:55:00'), # 完成
    ('郑凯', '京东', '京东物流优化', '2025-09-05', '2025-09-11', 0, 7, '京东物流优化', '2025-09-05 15:30:00', '2025-09-05T20:15:00'), # 待提交/草稿
    ('钱蓉', '字节跳动', '字节跳动推荐系统', '2025-07-01', '2025-07-07', 1, 7, '字节跳动推荐系统', '2025-07-01 10:40:00', '2025-07-01T15:05:00') # 审批中
]

cursor.executemany("""
    INSERT INTO travel (user_name, destination, reason, start_date, end_date, status, avg_working_hours, description, create_date, update_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test_travel_data)



# 请假表
cursor.execute('DROP TABLE IF EXISTS "leave";')

cursor.execute("""
CREATE TABLE "leave" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT,
    start_date DATE,
    end_date DATE,
    status INTEGER,
    description TEXT,
    create_date TIMESTAMP,
    update_date TIMESTAMP
);
""")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_leave_start_date ON leave(start_date)")

test_leave_data = [
    ('张三', '2024-03-15', '2024-03-18', 1, '生病',
     '2024-02-20 09:30:00', '2024-02-25T14:20:00'),
    ('李四', '2024-03-22', '2024-03-25', 0, '生病',
     '2024-02-25 10:15:00', '2024-02-25T10:15:00'),
    ('王五', '2024-04-01', '2024-04-05', 1, '生病',
     '2024-02-18 16:45:00', '2024-02-22T11:30:00'),
    ('赵六', '2024-03-10', '2024-03-12', 2, '生病',
     '2024-02-15 13:20:00', '2024-02-28T09:15:00'),
    ('钱七', '2024-04-08', '2024-04-11', 0, '生病',
     '2024-02-28 08:50:00', '2024-02-28T08:50:00'),
    ('孙八', '2024-03-28', '2024-03-31', 1, '生病',
     '2024-02-22 11:10:00', '2024-02-26T16:40:00'),
    ('周九', '2024-04-15', '2024-04-17', 0, '生病',
     '2024-02-27 14:25:00', '2024-02-27T14:25:00'),
    ('吴十', '2024-03-05', '2024-03-08', 1, '生病',
     '2024-02-16 15:30:00', '2024-02-24T10:05:00')
]

cursor.executemany("""
    INSERT INTO leave (user_name, start_date, end_date, status, description, create_date, update_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", test_leave_data)



# cursor.execute("PRAGMA table_info(attendance_token);")
# print(cursor.fetchall())

# 4. 提交并关闭连接
conn.commit()

conn.close()
