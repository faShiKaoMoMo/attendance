import sqlite3
from datetime import datetime

# 1. 连接数据库（没有的话会自动创建）
conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()



################################################## 课表
cursor.execute('DROP TABLE IF EXISTS "class";')
cursor.execute('DROP TABLE IF EXISTS "semester_class";')

cursor.execute("""
CREATE TABLE "semester_class" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    start_date DATE,
    end_date DATE,
    enable INTEGER,
    create_date TIMESTAMP,
    update_date TIMESTAMP
);
""")

cursor.execute("""
INSERT INTO semester_class (
    name,
    start_date,
    end_date,
    enable,
    create_date,
    update_date
) VALUES (
    '2025-2026 第一学期',
    '2025-09-01',
    '2025-12-28',
    1,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);
""")

cursor.execute('DROP TABLE IF EXISTS "semester_class_item";')

cursor.execute("""
CREATE TABLE "semester_class_item" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    semester_class_id INTEGER,
    name TEXT, -- 学生姓名
    week INTEGER, -- 0周一 1周二 2周三 3周四 4周五
    slot TEXT, -- 上课节次，例如 08:00 - 09:40
    type TEXT, -- 上课类型，all odd even
    create_date TIMESTAMP,
    update_date TIMESTAMP
);
""")

cursor.execute("CREATE INDEX idx_semester_class_item_semester_class_id ON semester_class_item (semester_class_id);")

sql = """
INSERT INTO semester_class_item VALUES (NULL,1,'吴清强',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',0,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴清强',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',0,'10:10 - 11:50','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',0,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',0,'14:30 - 16:10','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',0,'14:30 - 16:10','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',0,'14:30 - 16:10','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',0,'14:30 - 16:10','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',0,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',0,'14:30 - 16:10','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',0,'14:30 - 16:10','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'马可心',0,'14:30 - 16:10','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',0,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'邓椅文',0,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',0,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴清强',1,'08:00 - 09:40','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',1,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',1,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国英',1,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴清强',1,'10:10 - 11:50','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王美红',1,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',1,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'柯念昕',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',1,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'马可心',1,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',2,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',2,'08:00 - 09:40','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',2,'08:00 - 09:40','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',2,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',2,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',2,'08:00 - 09:40','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'陈思涵',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',2,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',2,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',2,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'马可心',2,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',2,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王黎明',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'马可心',2,'16:40 - 18:20','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',2,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',2,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国前',2,'19:10 - 20:50','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',2,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'聂鹏远',2,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'马可心',3,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',3,'10:10 - 11:50','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'梁楠',3,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',3,'16:40 - 18:20','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',3,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',3,'16:40 - 18:20','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',3,'16:40 - 18:20','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',3,'16:40 - 18:20','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',3,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国英',3,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',3,'16:40 - 18:20','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘成杨',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'赵婉茹',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘艳',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国英',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',3,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'林哲帆',4,'08:00 - 09:40','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'胡书豪',4,'08:00 - 09:40','even',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'杨雨辰',4,'08:00 - 09:40','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'王美红',4,'10:10 - 11:50','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'吴滢洁',4,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',4,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'黄宇鹏',4,'10:10 - 11:50','odd',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',4,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国英',4,'10:10 - 11:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',4,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',4,'14:30 - 16:10','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'刘国英',4,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',4,'16:40 - 18:20','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'向泽旭',4,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'范远生',4,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'谢一帆',4,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
INSERT INTO semester_class_item VALUES (NULL,1,'龚星月',4,'19:10 - 20:50','all',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);
"""
for line in sql.split('\n'):
    if line:
        cursor.execute(line)

rows = cursor.execute("""
SELECT *
FROM semester_class_item
WHERE semester_class_id IN (
    SELECT id
    FROM semester_class
    WHERE enable = 1
    ORDER BY id DESC
    LIMIT 1
);
""")
for row in rows:
    print(row)


################################################## 调课表




################################################## 出差表
cursor.execute('DROP TABLE IF EXISTS "travel";')

cursor.execute("""
CREATE TABLE "travel" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
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
    ('王文凯', '九牧', '九牧RPA', '2025-11-03', '2025-11-07', 1, 8, '九牧RPA', '2025-10-27 09:30:00',
     '2025-10-27T14:20:00'),
    ('王文凯', '九牧', '九牧RPA', '2025-11-11', '2025-11-12', 1, 8, '九牧RPA', '2025-10-27 09:30:00',
     '2025-10-27T14:20:00'),
]

cursor.executemany("""
    INSERT INTO travel (name, destination, reason, start_date, end_date, status, avg_working_hours, description, create_date, update_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test_travel_data)



################################################## 请假表
cursor.execute('DROP TABLE IF EXISTS "leave";')

cursor.execute("""
CREATE TABLE "leave" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
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
    ('王文凯', '2025-11-10', '2025-11-10', 1, '面试', '2025-11-09 09:30:00', '2025-11-09:30:00'),
]

cursor.executemany("""
    INSERT INTO leave (name, start_date, end_date, status, description, create_date, update_date)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", test_leave_data)



################################################## 清空爬虫记录
# cursor.execute("""
#     DELETE FROM attendance_statistics
# """)



conn.commit()
conn.close()
