import sqlite3
from datetime import datetime

# 1. 连接数据库（没有的话会自动创建）
conn = sqlite3.connect("attendance.db")  # 换成你的数据库文件名
cursor = conn.cursor()

# cursor.execute('DROP TABLE IF EXISTS "class";')
#
# cursor.execute("""
# CREATE TABLE "class" (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     content TEXT,
#     start_date DATE,
#     end_date DATE,
#     create_date TIMESTAMP,
#     update_date TIMESTAMP
# );
# """)
#
# data = """
# {
#     "0":[
#         {"time":["8:00","9:40"],"names":[["吴清强","all"],["刘国前","all"],["向泽旭","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"],["龚星月","all"]]},
#         {"time":["10:10","11:50"],"names":[["吴清强","all"],["刘成杨","all"],["刘国前","all"],["向泽旭","even"],["吴滢洁","all"],["黄宇鹏","all"],["林哲帆","all"],["赵婉茹","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
#         {"time":["14:30","16:10"],"names":[["刘成杨","odd"],["向泽旭","odd"],["吴滢洁","odd"],["赵婉茹","odd"],["范远生","all"],["王黎明","even"],["陈思涵","even"],["马可心","even"]]},
#         {"time":["16:40","18:20"],"names":[["刘国前","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"],["邓椅文","odd"]]},
#         {"time":["19:10","20:50"],"names":[["范远生","all"]]}
#     ],
#     "1":[
#         {"time":["8:00","9:40"],"names":[["吴清强","odd"],["刘成杨","all"],["赵婉茹","all"],["刘国英","all"]]},
#         {"time":["10:10","11:50"],"names":[["吴清强","odd"],["王美红","all"]]},
#         {"time":["14:30","16:10"],"names":[["刘国前","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
#         {"time":["16:40","18:20"],"names":[["刘成杨","all"],["刘国前","all"],["向泽旭","all"],["吴滢洁","all"],["柯念昕","all"],["黄宇鹏","all"],["林哲帆","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["聂鹏远","all"]]},
#         {"time":["19:10","20:50"],"names":[["马可心","all"]]}
#     ],
#     "2":[
#         {"time":["8:00","9:40"],"names":[["刘国前","all"],["黄宇鹏","even"],["林哲帆","even"],["赵婉茹","all"],["刘艳","all"],["陈思涵","all"]]},
#         {"time":["10:10","11:50"],"names":[["刘成杨","all"],["刘国前","all"],["向泽旭","all"],["吴滢洁","all"],["赵婉茹","all"],["王黎明","all"],["刘艳","all"],["陈思涵","all"],["谢一帆","all"],["龚星月","all"]]},
#         {"time":["14:30","16:10"],"names":[["赵婉茹","all"],["王黎明","all"],["马可心","all"],["谢一帆","all"]]},
#         {"time":["16:40","18:20"],"names":[["刘成杨","odd"],["向泽旭","odd"],["吴滢洁","odd"],["赵婉茹","odd"],["王黎明","odd"],["马可心","odd"],["谢一帆","all"],["龚星月","all"]]},
#         {"time":["19:10","20:50"],"names":[["刘国前","odd"],["吴滢洁","all"],["聂鹏远","all"]]}
#     ],
#     "3":[
#         {"time":["8:00","9:40"],"names":[]},
#         {"time":["10:10","11:50"],"names":[["马可心","all"],["龚星月","odd"]]},
#         {"time":["14:30","16:10"],"names":[["梁楠","all"]]},
#         {"time":["16:40","18:20"],"names":[["刘成杨","even"],["向泽旭","all"],["吴滢洁","even"],["赵婉茹","even"],["范远生","even"],["谢一帆","all"],["刘国英","all"],["龚星月","even"]]},
#         {"time":["19:10","20:50"],"names":[["刘成杨","all"],["向泽旭","all"],["吴滢洁","all"],["赵婉茹","all"],["范远生","all"],["刘艳","all"],["谢一帆","all"],["刘国英","all"],["龚星月","all"]]}
#     ],
#     "4":[
#         {"time":["8:00","9:40"],"names":[["林哲帆","odd"],["胡书豪","even"],["杨雨辰","odd"]]},
#         {"time":["10:10","11:50"],"names":[["王美红","odd"],["吴滢洁","all"],["范远生","all"],["黄宇鹏","odd"],["谢一帆","all"],["刘国英","all"]]},
#         {"time":["14:30","16:10"],"names":[["范远生","all"],["谢一帆","all"]]},
#         {"time":["16:40","18:20"],"names":[["刘国英","all"],["龚星月","all"]]},
#         {"time":["19:10","20:50"],"names":[["向泽旭","all"],["范远生","all"],["谢一帆","all"],["龚星月","all"]]}
#     ]
# }
# """
#
# cursor.execute("""
#     INSERT INTO class (content, start_date, end_date, create_date, update_date)
#     VALUES (?, ?, ?, ?, ?)
# """, (
#     data,
#     "2025-09-01",
#     "2025-12-28",
#     datetime.now().strftime("%Y-%m-%d"),
#     datetime.now().strftime("%Y-%m-%d")
# ))

#  出差表
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

test_travel_data = [(
    '张三', '北京', '商务会议', '2024-03-15', '2024-03-18', 1, 8, '参加年度技术峰会，与合作伙伴洽谈业务合作事宜',
    '2024-02-20 09:30:00', '2024-02-25T14:20:00'),
    ('李四', '上海', '技术培训', '2024-03-22', '2024-03-25', 0, 7, '参加AWS云计算架构师认证培训课程',
     '2024-02-25 10:15:00', '2024-02-25T10:15:00'),
    ('王五', '广州', '项目考察', '2024-04-01', '2024-04-05', 1, 6, '考察新项目场地，与当地供应商会面洽谈合作细节',
     '2024-02-18 16:45:00', '2024-02-22T11:30:00'),
    ('赵六', '成都', '客户拜访', '2024-03-10', '2024-03-12', 2, 7, '拜访重要客户，进行产品演示和需求调研',
     '2024-02-15 13:20:00', '2024-02-28T09:15:00'),
    ('钱七', '杭州', '行业展会', '2024-04-08', '2024-04-11', 0, 6, '参加国际人工智能博览会，了解行业最新发展趋势',
     '2024-02-28 08:50:00', '2024-02-28T08:50:00'),
    ('孙八', '西安', '团队建设', '2024-03-28', '2024-03-31', 1, 8, '组织部门团队建设活动，提升团队凝聚力',
     '2024-02-22 11:10:00', '2024-02-26T16:40:00'),
    ('周九', '深圳', '产品发布会', '2024-04-15', '2024-04-17', 0, 7, '参加公司新产品发布会，协助现场技术支持',
     '2024-02-27 14:25:00', '2024-02-27T14:25:00'),
    ('吴十', '南京', '学术交流', '2024-03-05', '2024-03-08', 1, 7.5,'参加全国计算机科学学术会议，发表研究成果',
     '2024-02-16 15:30:00', '2024-02-24T10:05:00')
]

cursor.executemany("""
    INSERT INTO travel (user_name, destination, reason, start_date, end_date, status, avg_working_hours, description, create_date, update_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", test_travel_data)

# cursor.execute("PRAGMA table_info(attendance_token);")
# print(cursor.fetchall())

# 4. 提交并关闭连接
conn.commit()

conn.close()
