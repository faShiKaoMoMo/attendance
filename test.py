import sqlite3
from datetime import datetime

# 1. 连接数据库（没有的话会自动创建）
conn = sqlite3.connect("attendance.db")  # 换成你的数据库文件名
cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS "class";')

cursor.execute("""
CREATE TABLE "class" (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT,
    start_date DATE,
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
    INSERT INTO class (content, start_date, create_date, update_date)
    VALUES (?, ?, ?, ?)
""", (
    data,
    "2025-09-01",          # 你的日期格式
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%Y-%m-%d")
))

# cursor.execute("PRAGMA table_info(attendance_token);")
# print(cursor.fetchall())

# 4. 提交并关闭连接
conn.commit()

conn.close()
