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


def get_week_type(current_date, ref_date=datetime(2025, 9, 1)):
    """判断给定日期是单周还是双周。"""
    ref_week = ref_date.isocalendar()[1]
    current_week = current_date.isocalendar()[1]
    week_difference = current_week - ref_week
    return 'odd' if week_difference % 2 == 0 else 'even'


def generate_class_schedule(start_date_str, end_date_str, raw_schedule):
    """根据原始课表数据、日期范围和单双周规则，生成最终的 class_schedule 字典。"""
    class_schedule = {}
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    current_date = start_date
    while current_date <= end_date:
        weekday = current_date.weekday()

        if weekday > 4:
            current_date += timedelta(days=1)
            continue

        week_type = get_week_type(current_date)

        # 注意：从JSON加载的key是字符串"0", "1"等，所以需要用 str(weekday) 查找
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

def get_day_checkin_times(checkin_records):
    """
    分析单日打卡记录，找出上、下午和晚上的签到和签退时间点。
    重构版：采用完全独立的、严格的时间窗口来搜索每个打卡点，逻辑清晰无误。
    """
    times_in_minutes = sorted([time_to_minutes(format_timestamp(r['checkin_time'])) for r in checkin_records])
    results = {'am_in': '-', 'am_out': '-', 'pm_in': '-', 'pm_out': '-', 'eve_in': '-', 'eve_out': '-'}

    # 初始化所有可能的时间点为-1
    am_in, am_out, pm_in, pm_out, eve_in, eve_out = -1, -1, -1, -1, -1, -1

    # --- 1. 在各自独立的窗口内搜索 ---

    # 上午上班 (最早的 7:30 - 9:30)
    for t in times_in_minutes:
        if 450 <= t <= 570:
            am_in = t
            break

    # 上午下班 (最晚的 9:30之后 - 13:30之前)
    for t in reversed(times_in_minutes):
        if 570 < t < 810:
            am_out = t
            break

    # 下午上班 (最早的 13:30 - 14:30)
    for t in times_in_minutes:
        if 810 <= t <= 870:
            pm_in = t
            break

    # 下午下班 (最晚的 14:30之后 - 18:30之前)
    for t in reversed(times_in_minutes):
        if 870 < t < 1110:
            pm_out = t
            break

    # 晚上上班 (最早的 18:30之后 - 23:30之前)
    for t in times_in_minutes:
        if 1110 <= t < 1410:
            eve_in = t
            break

    # 晚上下班 (最晚的 18:30之后 - 23:30之前)
    for t in reversed(times_in_minutes):
        if 1110 <= t < 1410:
            eve_out = t
            break

    # --- 2. 后处理与填充 ---

    # 如果晚上只有一个打卡记录，它会被eve_in和eve_out同时捕获
    # 在这种情况下，我们只把它当作上班卡，将下班卡置空
    if eve_in != -1 and eve_in == eve_out:
        eve_out = -1

    # 填充结果字典
    if am_in != -1: results['am_in'] = f"{am_in // 60:02d}:{am_in % 60:02d}"
    if am_out != -1: results['am_out'] = f"{am_out // 60:02d}:{am_out % 60:02d}"
    if pm_in != -1: results['pm_in'] = f"{pm_in // 60:02d}:{pm_in % 60:02d}"
    if pm_out != -1: results['pm_out'] = f"{pm_out // 60:02d}:{pm_out % 60:02d}"
    if eve_in != -1: results['eve_in'] = f"{eve_in // 60:02d}:{eve_in % 60:02d}"
    if eve_out != -1: results['eve_out'] = f"{eve_out // 60:02d}:{eve_out % 60:02d}"

    return results


####################################################################################################

def statistic_person(name, record_week, total_work_days, class_schedule):
    shouldbe_attendance_hours = total_work_days * 8
    result_person = {'姓名': name, "应该出勤(小时)": shouldbe_attendance_hours, '实际出勤(小时)': 0, '有效出勤天数': 0,
                     '是否达标': ''}
    total_hours = 0
    total_valid_days = 0

    # 辅助函数1：从时间字符串计算时长（小时）
    def get_duration_hours(start_str, end_str):
        start_min = time_to_minutes(start_str.split(' ')[0])
        end_min = time_to_minutes(end_str.split(' ')[0])
        if start_min != -1 and end_min != -1 and end_min > start_min:
            return (end_min - start_min) / 60
        return 0

    # 辅助函数2：将分钟数格式化为 HH:MM 字符串
    def format_minutes_to_time(minutes):
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    for record_day in record_week:
        checkin_date = record_day['checkin_date']
        day_str = format_datetime(checkin_date)
        checkin_time_records = record_day['month_day_data']

        # 1. 获取物理打卡时间，并以此作为显示的默认值
        physical_times = get_day_checkin_times(checkin_time_records)
        display_times = physical_times.copy()

        # 2. 计算各时段的【物理打卡】时长
        physical_duration_am = get_duration_hours(physical_times['am_in'], physical_times['am_out'])
        physical_duration_pm = get_duration_hours(physical_times['pm_in'], physical_times['pm_out'])
        physical_duration_eve = get_duration_hours(physical_times['eve_in'], physical_times['eve_out'])

        # 3. 初始化各时段的【课程】时长和时间范围
        course_duration_am, course_duration_pm, course_duration_eve = 0, 0, 0
        am_course_bounds, pm_course_bounds, eve_course_bounds = [], [], []

        # 4. 检查并累加当天所有课程的时长
        person_schedule = class_schedule.get(name, {})
        day_classes = person_schedule.get(checkin_date, [])

        if day_classes:
            for course in day_classes:
                start_min = time_to_minutes(course['start'])
                end_min = time_to_minutes(course['end'])

                if start_min == -1 or end_min == -1 or end_min <= start_min:
                    continue

                duration = (end_min - start_min) / 60

                if start_min < 810:
                    course_duration_am += duration
                    am_course_bounds.append((start_min, end_min))
                elif 810 <= start_min < 1110:
                    course_duration_pm += duration
                    pm_course_bounds.append((start_min, end_min))
                else:
                    course_duration_eve += duration
                    eve_course_bounds.append((start_min, end_min))

        # 5. 【核心逻辑】比较时长，并根据胜出者决定【有效工时】和【显示内容】

        # --- 上午 ---
        effective_am_hours = physical_duration_am
        if course_duration_am > physical_duration_am:
            effective_am_hours = course_duration_am
            min_start = min(b[0] for b in am_course_bounds)
            max_end = max(b[1] for b in am_course_bounds)
            display_times['am_in'] = f"{format_minutes_to_time(min_start)} (课)"
            display_times['am_out'] = f"{format_minutes_to_time(max_end)} (课)"

        # --- 下午 ---
        effective_pm_hours = physical_duration_pm
        if course_duration_pm > physical_duration_pm:
            effective_pm_hours = course_duration_pm
            min_start = min(b[0] for b in pm_course_bounds)
            max_end = max(b[1] for b in pm_course_bounds)
            display_times['pm_in'] = f"{format_minutes_to_time(min_start)} (课)"
            display_times['pm_out'] = f"{format_minutes_to_time(max_end)} (课)"

        # --- 晚上 ---
        effective_eve_hours = physical_duration_eve
        if course_duration_eve > physical_duration_eve:
            effective_eve_hours = course_duration_eve
            min_start = min(b[0] for b in eve_course_bounds)
            max_end = max(b[1] for b in eve_course_bounds)
            display_times['eve_in'] = f"{format_minutes_to_time(min_start)} (课)"
            display_times['eve_out'] = f"{format_minutes_to_time(max_end)} (课)"

        # 6. 累加当天总有效工时
        day_total_hours = effective_am_hours + effective_pm_hours + effective_eve_hours
        total_hours += day_total_hours

        # 7. 存储最终要显示的内容
        result_person[day_str] = display_times

        # 8. “有效天数”判断
        if effective_am_hours > 0 and effective_pm_hours > 0:
            total_valid_days += 1

    # 汇总并返回结果
    total_hours = round(total_hours, 2)
    result_person['实际出勤(小时)'] = total_hours
    result_person['有效出勤天数'] = total_valid_days
    result_person['是否达标'] = '是' if total_hours >= shouldbe_attendance_hours else '否'
    return result_person


####################################################################################################

def statistic(infos, start_date, end_date, class_schedule, workday_count, exclude_person=None):
    result = []

    for person_info in infos:
        name = person_info['member_name'].strip()
        if exclude_person and name in exclude_person:
            continue
        try:
            result.append(statistic_person(name, person_info['month_days'], workday_count, class_schedule))
        except Exception as e:
            traceback.print_exc()
            print(f"处理 '{person_info['member_name']}' 数据时出错: {e}")
    return result


####################################################################################################

def fetch(conn, cursor, token, req_data):
    start_date = req_data['start_date']
    end_date = req_data['end_date']
    attendance_days = req_data['attendance_days']

    # 课表
    cursor.execute('SELECT content FROM `class` ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    class_info = generate_class_schedule(start_date, end_date, json.loads(row[0]))

    # 实验室
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

    # 统计
    data_list = []
    for toke in token:
        lab = toke['name']
        if lab in lab_info:
            exclude_person = lab_info[lab]
        else:
            exclude_person = []

        data = fetchdata(start_date, end_date, toke['Authorization'], toke['org_id'], toke['member_id'])
        data = statistic(data, start_date, end_date, class_schedule=class_info, workday_count=attendance_days, exclude_person=exclude_person)
        data_list.extend(data)

    return data_list
