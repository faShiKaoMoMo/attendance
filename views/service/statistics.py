import json
import sys
import traceback
from datetime import datetime, timedelta

import openpyxl
import requests
from openpyxl.styles import Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def format_datetime(date_str):
    date_obj = datetime.strptime(date_str, "%Y%m%d")
    formatted_date = date_obj.strftime("%m-%d")
    return formatted_date


def format_timestamp(timestamp):
    return datetime.fromtimestamp(int(timestamp) / 1000).strftime("%H:%M")


def time_to_minutes(time_str):
    if time_str == '-':
        return -1  # Return a value that indicates missing data
    hours, minutes = map(int, time_str.split(":"))
    return hours * 60 + minutes


def minutes_to_time_str(minutes):
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


####################################################################################################

def load_raw_schedule_from_json(filename="schedule.json"):
    """从指定的JSON文件加载原始课表数据。"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(1)  # 退出程序
    except json.JSONDecodeError:
        sys.exit(1)  # 退出程序


def get_week_type(current_date, ref_date):
    """
    判断给定日期是单周还是双周。
    基于 ref_date (开学第一周) 计算。
    """
    # 兼容处理：如果传入的是 date 对象 (mysql date类型)，转为 datetime
    if not isinstance(ref_date, datetime):
        if hasattr(ref_date, 'year'):
            ref_date = datetime(ref_date.year, ref_date.month, ref_date.day)
        else:
            # 如果是其他异常类型，默认一个兜底时间，防止报错
            ref_date = datetime(2025, 9, 1)

    ref_week = ref_date.isocalendar()[1]
    current_week = current_date.isocalendar()[1]

    # 简单的周次差计算
    # 注意：如果跨年，isocalendar()[1] 会重置，这里简单处理假设学期内不跨非常大的年份周期
    # 或者如果跨年，需要更复杂的 (date-ref).days // 7 逻辑
    # 保持原有逻辑风格：
    week_difference = current_week - ref_week

    return 'odd' if week_difference % 2 == 0 else 'even'


def generate_class_schedule(start_date_str, end_date_str, raw_schedule, semester_start_input):
    """根据原始课表数据、日期范围和单双周规则，生成最终的 class_schedule 字典。"""
    class_schedule = {}
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    # --- 处理开学基准时间 ---
    # 默认为 2025-09-01，防止数据库字段为空或格式错误
    ref_date = datetime(2025, 9, 1)

    if semester_start_input:
        if isinstance(semester_start_input, str):
            try:
                if '-' in semester_start_input:
                    ref_date = datetime.strptime(semester_start_input, "%Y-%m-%d")
                else:
                    ref_date = datetime.strptime(semester_start_input, "%Y%m%d")
            except ValueError:
                print(f"日期格式解析错误: {semester_start_input}，使用默认值")
        elif isinstance(semester_start_input, datetime):
            ref_date = semester_start_input
        elif hasattr(semester_start_input, 'year'):  # 处理 datetime.date 对象
            ref_date = datetime(semester_start_input.year, semester_start_input.month, semester_start_input.day)

    current_date = start_date
    while current_date <= end_date:
        weekday = current_date.weekday()

        if weekday > 4:
            current_date += timedelta(days=1)
            continue

        # 传入计算出的 ref_date
        week_type = get_week_type(current_date, ref_date)

        # 从JSON加载的key是字符串"0", "1"等
        day_schedule = raw_schedule.get(str(weekday), [])

        for course in day_schedule:
            start_time, end_time = course['time']

            for person_name, required_week_type in course['names']:
                if required_week_type == 'all' or required_week_type == week_type:
                    date_key = current_date.strftime("%Y%m%d")
                    course_info = {'start': start_time, 'end': end_time}

                    if person_name not in class_schedule:
                        class_schedule[person_name] = {}
                    if date_key not in class_schedule[person_name]:
                        class_schedule[person_name][date_key] = []

                    class_schedule[person_name][date_key].append(course_info)

        current_date += timedelta(days=1)

    return class_schedule


####################################################################################################

def fetchdata(start_date, end_date, token, org_id, member_id):
    url = 'https://checkin2-app.delicloud.com/ass/api/v2.0/schedule/findMonthReport'
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Authorization': token,
        'Connection': 'keep-alive',
        'Content-Type': 'application/json;charset=UTF-8',
        'Host': 'checkin2-app.delicloud.com',
        'Origin': 'https://v2-eapp.delicloud.com',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
        'X-Service-Id': 'ass-report',
        'client_id': 'eplus_web',
        'member_id': member_id,
        'org_id': org_id,
        'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Microsoft Edge";v="128"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    start_date_before = (datetime.strptime(start_date, "%Y%m%d")).strftime("%Y%m%d")
    end_date_after = (datetime.strptime(end_date, "%Y%m%d")).strftime("%Y%m%d")
    data = {"org_id": org_id, "start_date": start_date_before, "end_date": end_date_after, "dept_ids": [],
            "member_ids": [], "page": 1, "size": 50, "order": 0}
    response = requests.post(url, headers=headers, json=data)
    return response.json()['data']['rows']


####################################################################################################

def statistic_person(name, record_week, total_work_days, class_schedule):
    # 1. 初始化字典
    result_person = {'姓名': name}

    total_hours = 0
    total_valid_days = 0

    # 遍历每一天
    for record_day in record_week:
        checkin_date = record_day['checkin_date']
        day_str = format_datetime(checkin_date)
        checkin_time_records = record_day['month_day_data']

        # --- 收集时间点 (Points) ---
        am_points = []
        pm_points = []
        eve_points = []

        # 1.1 物理打卡点
        for r in checkin_time_records:
            t_str = format_timestamp(r['checkin_time'])
            t_min = time_to_minutes(t_str)
            point = (t_min, 'phys')
            if t_min < 810:
                am_points.append(point)
            elif 810 <= t_min < 1110:
                pm_points.append(point)
            else:
                eve_points.append(point)

        # 1.2 课程时间点
        person_schedule = class_schedule.get(name, {})
        day_classes = person_schedule.get(checkin_date, [])
        if day_classes:
            for course in day_classes:
                start_min = time_to_minutes(course['start'])
                end_min = time_to_minutes(course['end'])
                if start_min == -1 or end_min == -1: continue

                if start_min < 810:
                    am_points.append((start_min, 'class'))
                    am_points.append((end_min, 'class'))
                elif 810 <= start_min < 1110:
                    pm_points.append((start_min, 'class'))
                    pm_points.append((end_min, 'class'))
                else:
                    eve_points.append((start_min, 'class'))
                    eve_points.append((end_min, 'class'))

        # --- 处理各时段 ---
        display_times = {'am_in': '-', 'am_out': '-', 'pm_in': '-', 'pm_out': '-', 'eve_in': '-', 'eve_out': '-'}

        def process_points(points):
            if not points: return 0, '-', '-'
            sorted_points = sorted(points, key=lambda x: x[0])
            first, last = sorted_points[0], sorted_points[-1]
            duration = (last[0] - first[0]) / 60 if last[0] > first[0] else 0

            s_str = minutes_to_time_str(first[0]) + (" (课)" if first[1] == 'class' else "")
            e_str = minutes_to_time_str(last[0]) + (" (课)" if last[1] == 'class' else "")
            if first[0] == last[0]: e_str = '-'
            return duration, s_str, e_str

        eff_am, display_times['am_in'], display_times['am_out'] = process_points(am_points)
        eff_pm, display_times['pm_in'], display_times['pm_out'] = process_points(pm_points)
        eff_eve, display_times['eve_in'], display_times['eve_out'] = process_points(eve_points)

        # 汇总
        total_hours += eff_am + eff_pm + eff_eve
        result_person[day_str] = display_times  # 记录当天的打卡详情

        if eff_am > 0 and eff_pm > 0:
            total_valid_days += 1

    # --- 2. 统计字段计算 ---
    total_hours = round(total_hours, 2)

    avg_daily_hours = 0
    if total_work_days > 0:
        avg_daily_hours = round(total_hours / total_work_days, 2)

    result_person['实际出勤时长'] = total_hours
    result_person['日均考勤时长'] = avg_daily_hours
    result_person['有效出勤天数'] = total_valid_days

    return result_person


####################################################################################################

def statistic(infos, start_date, end_date, class_schedule, workday_count, exclude_person=None):
    result = []

    for person_info in infos:
        name = person_info['member_name'].strip()
        if exclude_person and name in exclude_person:
            continue
        try:
            result.append(
                statistic_person(name, person_info['month_days'], workday_count, class_schedule))
        except Exception as e:
            traceback.print_exc()
            print(f"处理 '{person_info['member_name']}' 数据时出错: {e}")
    return result


####################################################################################################

def fetch(conn, cursor, token, req_data):
    start_date = req_data['start_date']
    end_date = req_data['end_date']
    attendance_days = req_data['attendance_days']  # 应出勤天数

    # 1. 获取课表和开学时间
    # 【修改】：增加查询 start_date
    cursor.execute('SELECT content, start_date FROM `class` ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()

    raw_schedule = {}
    semester_start = None

    if row:
        # 防止内容为空
        raw_schedule = json.loads(row[0]) if row[0] else {}
        # 读取开学日期 (假设是 row[1])
        semester_start = row[1]

    # 【修改】：传入 semester_start
    class_info = generate_class_schedule(start_date, end_date, raw_schedule, semester_start)

    # 2. 获取实验室配置 (排除名单)
    cursor.execute('SELECT * FROM attendance_config ORDER BY id DESC')
    rows = cursor.fetchall()
    lab_info = {}
    for row in rows:
        excluded_list = []
        if row["excluded_name"]:
            try:
                excluded_list = json.loads(row["excluded_name"])
            except Exception:
                excluded_list = [name.strip() for name in row["excluded_name"].split(',') if name.strip()]
        lab_info[row["lab"]] = excluded_list

    # 3. 统计所有数据
    data_list = []
    for toke in token:
        lab = toke['name']
        exclude_person = lab_info.get(lab, [])

        # 获取原始打卡数据
        raw_data = fetchdata(start_date, end_date, toke['Authorization'], toke['org_id'], toke['member_id'])

        # 处理单人统计
        processed_data = statistic(raw_data, start_date, end_date,
                                   class_schedule=class_info,
                                   workday_count=attendance_days,
                                   exclude_person=exclude_person)
        data_list.extend(processed_data)

    # 排序与排名

    # 根据 '实际出勤时长' 进行降序排序
    data_list.sort(key=lambda x: x['实际出勤时长'], reverse=True)

    # 添加排名并调整字段顺序
    final_list = []
    for index, person_data in enumerate(data_list):
        ordered_data = {'排名': index + 1}
        ordered_data.update(person_data)
        final_list.append(ordered_data)

    return final_list