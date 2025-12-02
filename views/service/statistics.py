import json
import sys
import traceback
from collections import defaultdict
from datetime import datetime, timedelta

import requests


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


def generate_class_schedule(start_date_str, end_date_str, raw_schedule, semester_start_input, semester_end_input):
    """
    根据原始课表数据、日期范围和单双周规则，生成最终的 class_schedule 字典。
    新增 semester_end_input 用于判断学期是否结束。
    """
    class_schedule = {}
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    # --- 处理开学基准时间 (Start) ---
    ref_date = datetime(2025, 9, 1)  # 默认值
    if semester_start_input:
        ref_date = parse_flexible_date(semester_start_input, ref_date)

    # --- 处理学期结束时间 (End) ---
    # 默认为很久以后，确保如果不传结束时间，默认课程一直有效
    ref_end_date = datetime(2099, 12, 31)
    if semester_end_input:
        ref_end_date = parse_flexible_date(semester_end_input, ref_end_date)

    current_date = start_date
    while current_date <= end_date:
        # 【关键修改】如果当前统计日期 已经超过了 学期结束日期，则跳过生成课程
        # 注意：这里比较的是 datetime 对象
        if current_date > ref_end_date:
            current_date += timedelta(days=1)
            continue

        weekday = current_date.weekday()

        if weekday > 4:  # 周六周日跳过
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


# 抽取了一个辅助函数来处理日期的各种格式，让主代码更干净
def parse_flexible_date(date_input, default_val):
    if isinstance(date_input, str):
        try:
            if '-' in date_input:
                return datetime.strptime(date_input, "%Y-%m-%d")
            else:
                return datetime.strptime(date_input, "%Y%m%d")
        except ValueError:
            return default_val
    elif isinstance(date_input, datetime):
        return date_input
    elif hasattr(date_input, 'year'):  # datetime.date 对象
        return datetime(date_input.year, date_input.month, date_input.day)
    return default_val


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

def statistic_person(name, record_week, total_work_days, class_schedule, travel_dates, leave_dates):
    # --- 配置常量 (分钟) ---
    # AM: 7:30(450) - 9:30(570) 必须在此区间签到
    AM_WINDOW_START = 450
    AM_WINDOW_END = 570
    AM_SPLIT = 810  # 13:30 分界线

    # PM: 13:30(810) - 14:30(870) 必须在此区间签到
    PM_WINDOW_START = 810
    PM_WINDOW_END = 870
    PM_SPLIT = 1110  # 18:30 分界线

    # Eve: 18:30(1110) - 23:30(1410)
    EVE_CHECKOUT_LIMIT = 1410

    # 1. 初始化结果
    result_person = {'姓名': name}
    total_hours = 0
    total_valid_days = 0

    # 遍历每一天
    for record_day in record_week:
        checkin_date = record_day['checkin_date']  # 格式通常为 "20240901"
        day_str = format_datetime(checkin_date)  # 格式为 "09-01"

        # 将 checkin_date (如 "20240901") 转为 "2024-09-01"
        try:
            current_date_obj = datetime.strptime(str(checkin_date), "%Y%m%d")
            check_date_str = current_date_obj.strftime("%Y-%m-%d")
        except:
            check_date_str = ""

        if check_date_str in leave_dates:
            # 1. 当天标记为(请假)
            display_times = {
                'am_in': '(请假)', 'am_out': '(请假)',
                'pm_in': '(请假)', 'pm_out': '(请假)',
                'eve_in': '(请假)', 'eve_out': '(请假)'
            }
            result_person[day_str] = display_times

            # 2. 无考勤：不累加 total_hours，不算有效出勤天数
            # 3. 跳过后续常规打卡计算
            continue

        if check_date_str in travel_dates:
            # 如果是出差日：
            # 1. 当天标记为(出差)
            display_times = {
                'am_in': '(出差)', 'am_out': '(出差)',
                'pm_in': '(出差)', 'pm_out': '(出差)',
                'eve_in': '(出差)', 'eve_out': '(出差)'
            }
            result_person[day_str] = display_times

            # 2. 考勤时间为0 (不累加到 total_hours)

            # 3. 算上有效出勤
            total_valid_days += 1

            # 4. 跳过后续常规打卡计算
            continue

        # 获取物理打卡时间
        raw_checkin_records = record_day.get('month_day_data', [])

        # 获取课程时间
        person_schedule = class_schedule.get(name, {})
        day_classes = person_schedule.get(checkin_date, [])

        # --- 1. 收集所有时间点并归类 ---
        am_points = []
        pm_points = []
        eve_points = []

        # (A) 处理物理打卡
        for r in raw_checkin_records:
            t_str = format_timestamp(r['checkin_time'])
            t_min = time_to_minutes(t_str)
            if t_min == -1:
                continue

            point = (t_min, 'phys')

            # 分桶
            if t_min < AM_SPLIT:
                am_points.append(point)
            elif AM_SPLIT <= t_min < PM_SPLIT:
                pm_points.append(point)
            else:
                eve_points.append(point)

        # (B) 处理课程时间 (有课自动算打卡)
        for course in day_classes:
            start_min = time_to_minutes(course['start'])
            end_min = time_to_minutes(course['end'])
            if start_min == -1 or end_min == -1:
                continue

            # 课程起止点都加入
            p_start = (start_min, 'class')
            p_end = (end_min, 'class')

            # 课程开始归类
            if start_min < AM_SPLIT:
                am_points.append(p_start)
            elif start_min < PM_SPLIT:
                pm_points.append(p_start)
            else:
                eve_points.append(p_start)

            # 课程结束归类
            if end_min < AM_SPLIT:
                am_points.append(p_end)
            elif end_min < PM_SPLIT:
                pm_points.append(p_end)
            else:
                eve_points.append(p_end)

        # --- 2. 核心计算逻辑 ---
        def calculate_session(points, start_min_limit, start_max_limit, end_hard_limit=None):
            if not points:
                return 0, '-', '-'

            # 1. 分离物理打卡点和课程点
            phys_points = sorted([p for p in points if p[1] == 'phys'], key=lambda x: x[0])
            class_points = sorted([p for p in points if p[1] == 'class'], key=lambda x: x[0])

            valid_start_time = None
            start_source = None  # 用于标记来源 ('phys' 或 'class')

            # --- A. 尝试寻找有效的物理打卡 ---
            if phys_points:
                first_phys = phys_points[0]
                is_phys_valid = True

                # 如果有时间窗口限制（上午/下午），检查是否越界
                if start_min_limit is not None and start_max_limit is not None:
                    if not (start_min_limit <= first_phys[0] <= start_max_limit):
                        is_phys_valid = False

                # 如果物理打卡有效，优先采用
                if is_phys_valid:
                    valid_start_time = first_phys[0]
                    start_source = 'phys'

            # --- B. 如果没有有效物理打卡(迟到/缺卡)，检查是否有课兜底 ---
            if valid_start_time is None and class_points:
                # 只要有课，就视为出勤，并使用上课时间作为开始时间
                valid_start_time = class_points[0][0]
                start_source = 'class'

            # --- C. 最终校验起点 ---
            if valid_start_time is None:
                return 0, '-', '-'

            # --- D. 确定结束时间 ---
            all_sorted = sorted(points, key=lambda x: x[0])
            end_time = all_sorted[-1][0]
            end_source = all_sorted[-1][1]

            # --- E. 校验晚上签退硬限制 ---
            if end_hard_limit is not None and end_time > end_hard_limit:
                return 0, '-', '-'

            start_str = minutes_to_time_str(valid_start_time) + ("(课)" if start_source == 'class' else "")

            # --- F. 校验单次打卡 ---
            if valid_start_time == end_time:
                return 0, start_str, '-'

            # --- G. 正常计算 ---
            duration = (end_time - valid_start_time) / 60.0
            end_str = minutes_to_time_str(end_time) + ("(课)" if end_source == 'class' else "")

            return duration, start_str, end_str

        # --- 3. 分别计算三个时段 ---
        eff_am, am_in, am_out = calculate_session(am_points, AM_WINDOW_START, AM_WINDOW_END)
        eff_pm, pm_in, pm_out = calculate_session(pm_points, PM_WINDOW_START, PM_WINDOW_END)
        eff_eve, eve_in, eve_out = calculate_session(eve_points, None, None, end_hard_limit=EVE_CHECKOUT_LIMIT)

        # 汇总
        day_total = eff_am + eff_pm + eff_eve
        total_hours += day_total

        # 记录
        display_times = {
            'am_in': am_in, 'am_out': am_out,
            'pm_in': pm_in, 'pm_out': pm_out,
            'eve_in': eve_in, 'eve_out': eve_out
        }
        result_person[day_str] = display_times

        # 有效天数
        if eff_am > 0 and eff_pm > 0:
            total_valid_days += 1

    # --- 4. 最终统计 (此处只包含“实际出勤”) ---
    total_hours = round(total_hours, 2)
    avg_daily_hours = 0
    if total_work_days > 0:
        avg_daily_hours = round(total_hours / total_work_days, 2)

    result_person['实际出勤时长'] = total_hours
    result_person['日均考勤时长'] = avg_daily_hours
    result_person['有效出勤天数'] = total_valid_days

    return result_person


####################################################################################################

def statistic(infos, start_date, end_date, class_schedule, workday_count, travel_map, leave_map, exclude_person=None):
    """
    增加了 travel_map 和 leave_map 参数
    """
    result = []

    for person_info in infos:
        name = person_info['member_name'].strip()
        if exclude_person and name in exclude_person:
            continue
        try:
            # 获取该人的出差日期集合
            person_travel_dates = travel_map.get(name, set())
            # 获取该人的请假日期集合
            person_leave_dates = leave_map.get(name, set())

            result.append(
                statistic_person(
                    name,
                    person_info['month_days'],
                    workday_count,
                    class_schedule,
                    person_travel_dates,  # 出差日期
                    person_leave_dates  # 请假日期
                )
            )
        except Exception as e:
            traceback.print_exc()
            print(f"处理 '{person_info['member_name']}' 数据时出错: {e}")
    return result


####################################################################################################

def fetch(conn, cursor, token, req_data):
    start_date = req_data['start_date']
    end_date = req_data['end_date']
    attendance_days = req_data['attendance_days']  # 应出勤天数

    start_date_format = datetime.strptime(start_date, "%Y%m%d").date()
    end_date_format = datetime.strptime(end_date, "%Y%m%d").date()

    # 1. 获取课表和开学时间
    cursor.execute('SELECT content, start_date, end_date FROM `class` ORDER BY id DESC LIMIT 1')
    rows = cursor.fetchone()
    raw_schedule = {}
    semester_start = None
    semester_end = None
    if rows:
        raw_schedule = json.loads(rows[0]) if rows[0] else {}
        semester_start = rows[1]
        semester_end = rows[2]
    class_info = generate_class_schedule(start_date, end_date, raw_schedule, semester_start, semester_end)

    # 2. 获取出差记录
    cursor.execute("""
        SELECT name, start_date, end_date, avg_working_hours
        FROM "travel"
        WHERE status = 1 
          AND start_date <= ? 
          AND end_date >= ?
    """, (end_date_format, start_date_format))
    rows = cursor.fetchall()
    travel_map = defaultdict(set)
    working_hour = {}
    for user_name, start_str, end_str, avg_working_hours in rows:
        # 字符串转日期
        trip_start = datetime.strptime(start_str, '%Y-%m-%d').date()
        trip_end = datetime.strptime(end_str, '%Y-%m-%d').date()
        # 实际统计开始 = max(出差开始, 查询开始)
        calc_start = max(trip_start, start_date_format)
        # 实际统计结束 = min(出差结束, 查询结束)
        calc_end = min(trip_end, end_date_format)
        # 计算该段出差在查询范围内的天数
        days_in_range = 0
        current_date = calc_start
        while current_date <= calc_end:
            travel_map[user_name].add(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
            days_in_range += 1
        # 累加出差补录时长 (天数 * 日均工时)
        current_total = working_hour.get(user_name, 0)
        working_hour[user_name] = current_total + (avg_working_hours * days_in_range)

    # 3. 获取请假记录
    cursor.execute("""
        SELECT name, start_date, end_date
        FROM "leave"
        WHERE status = 1 
          AND start_date <= ? 
          AND end_date >= ?
    """, (end_date_format, start_date_format))
    rows = cursor.fetchall()
    leave_map = defaultdict(set)
    for user_name, start_str, end_str in rows:
        # 字符串转日期
        trip_start = datetime.strptime(start_str, '%Y-%m-%d').date()
        trip_end = datetime.strptime(end_str, '%Y-%m-%d').date()
        # 实际统计开始 = max(请假开始, 查询开始)
        calc_start = max(trip_start, start_date_format)
        # 实际统计结束 = min(请假结束, 查询结束)
        calc_end = min(trip_end, end_date_format)
        current_date = calc_start
        while current_date <= calc_end:
            leave_map[user_name].add(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

    # 4. 获取实验室配置 (排除名单)
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

    # 5. 统计所有数据
    data_list = []
    for toke in token:
        lab = toke['name']
        exclude_person = lab_info.get(lab, [])

        # 获取原始打卡数据
        raw_data = fetchdata(start_date, end_date, toke['Authorization'], toke['org_id'], toke['member_id'])

        # 处理单人统计 (传入 travel_map 和 leave_map)
        processed_data = statistic(
            raw_data,
            start_date,
            end_date,
            class_schedule=class_info,
            workday_count=attendance_days,
            travel_map=travel_map,
            leave_map=leave_map,
            exclude_person=exclude_person
        )
        data_list.extend(processed_data)

    # 6. 后处理：计算最终时长、排序
    final_list = []
    for person_data in data_list:
        name = person_data['姓名']

        # 获取基础数据
        actual_hours = person_data.get('实际出勤时长', 0)

        # 获取出差补录时长
        travel_add_hours = working_hour.get(name, 0)

        # 计算最终出勤时长
        final_total_hours = actual_hours + travel_add_hours

        # 重新计算日均考勤时长 (基于最终时长)
        new_avg_daily = 0
        if attendance_days > 0:
            new_avg_daily = round(final_total_hours / attendance_days, 2)

        # 更新/新增字段
        person_data['出差补录时长'] = round(travel_add_hours, 2)
        person_data['最终出勤时长'] = round(final_total_hours, 2)
        person_data['日均考勤时长'] = new_avg_daily

    # 根据 '最终出勤时长' 进行降序排序
    data_list.sort(key=lambda x: x['最终出勤时长'], reverse=True)

    # 添加排名并调整顺序
    for index, person_data in enumerate(data_list):
        ordered_data = {'排名': index + 1}
        ordered_data.update(person_data)
        final_list.append(ordered_data)

    return final_list

