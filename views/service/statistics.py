import json
import sys
import traceback
from collections import defaultdict
from datetime import datetime, timedelta

import requests

from views.enums.enums import ClassTypeEnum


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


def get_week_type(current_date, ref_date):
    """
    判断给定日期是单周还是双周。
    基于 ref_date (开学第一周) 计算。
    修复：使用 (日期差 // 7) 逻辑，彻底解决跨年导致的周次重置问题。
    """
    # 1. 兼容处理：确保 ref_date 是 datetime 对象
    if not isinstance(ref_date, datetime):
        if hasattr(ref_date, 'year'):
            ref_date = datetime(ref_date.year, ref_date.month, ref_date.day)
        else:
            raise Exception("找不到学期课表")

    # 2. 兼容处理：确保 current_date 是 datetime 对象
    if not isinstance(current_date, datetime):
        if hasattr(current_date, 'year'):
            current_date = datetime(current_date.year, current_date.month, current_date.day)

    # 3. 核心逻辑修复：
    # 将两个日期都“对齐”到它们所在周的【周一】
    # weekday(): 周一=0, ... 周日=6
    ref_monday = ref_date - timedelta(days=ref_date.weekday())
    current_monday = current_date - timedelta(days=current_date.weekday())

    # 计算两个周一之间的天数差
    days_diff = (current_monday - ref_monday).days

    # 计算周次差 (整除7)
    week_difference = days_diff // 7

    # 4. 返回结果
    # 0 (即开学当周) 视为 ODD (单周)
    return ClassTypeEnum.ODD.code if week_difference % 2 == 0 else ClassTypeEnum.EVEN.code


def generate_class_schedule(start_date_str, end_date_str, items, semester_start_input, semester_end_input, override_map):
    """
    生成课表。
    新增参数: override_map (dict)，用于处理调休和节假日。
    结构: {'20251001': {'type': 'holiday'}, '20250928': {'type': 'swap', 'swap_date': datetime_obj}}
    """
    class_schedule = {}
    start_date = datetime.strptime(start_date_str, "%Y%m%d")
    end_date = datetime.strptime(end_date_str, "%Y%m%d")

    # 学期起止
    ref_date = datetime(2025, 9, 1)
    if semester_start_input:
        ref_date = parse_flexible_date(semester_start_input, ref_date)

    ref_end_date = datetime(2099, 12, 31)
    if semester_end_input:
        ref_end_date = parse_flexible_date(semester_end_input, ref_end_date)

    # 解析 slot
    parsed_items = []
    for it in items:
        try:
            start_t, end_t = [t.strip() for t in it["slot"].split("-")]
            parsed_items.append({
                "name": it["name"],
                "week": int(it["week"]),  # 0-6
                "start": start_t,
                "end": end_t,
                "type": it["type"]
            })
        except:
            continue

    # 开始按天生成课表
    current_date = start_date
    while current_date <= end_date:

        if current_date > ref_end_date:
            break

        date_key = current_date.strftime("%Y%m%d")

        # 默认逻辑日期 = 物理日期
        logic_date = current_date
        is_holiday = False

        # 检查 override 配置
        if date_key in override_map:
            setting = override_map[date_key]
            if setting['type'] == 'holiday':
                is_holiday = True
            elif setting['type'] == 'swap':
                # 如果是调休，课表逻辑使用 swap_date (例如周日补周二的课，逻辑日期就是周二那天)
                logic_date = setting.get('swap_date', current_date)

        # 1. 如果是节假日，直接跳过排课
        if is_holiday:
            current_date += timedelta(days=1)
            continue

        # 2. 获取【逻辑日期】的星期几
        # 如果是调休(周日补周二)，这里 weekday=1 (周二)
        weekday = logic_date.weekday()

        # 3. 这里的过滤逻辑基于【逻辑日期】
        # 如果今天是周日(Phys)，但调休补周二(Logic)，weekday=1，不会被 skip，会正常排课
        if weekday >= 5:
            current_date += timedelta(days=1)
            continue

        # 4. 获取【逻辑日期】的单双周类型
        week_type = get_week_type(logic_date, ref_date)

        # === 核心修改逻辑 End ===

        for it in parsed_items:
            # 匹配 逻辑日期 的星期
            if it["week"] != weekday:
                continue

            # 匹配 逻辑日期 的单双周
            if it["type"] != ClassTypeEnum.ALL.code and it["type"] != week_type:
                continue

            # 写入结构 (Key 依然是 date_key 即物理日期)
            person = it["name"]
            course_info = {
                "start": it["start"],
                "end": it["end"]
            }

            class_schedule.setdefault(person, {})
            class_schedule[person].setdefault(date_key, [])
            class_schedule[person][date_key].append(course_info)

        current_date += timedelta(days=1)

    return class_schedule


def calculate_standard_work_days(start_date_str, end_date_str, holiday_dates, swap_dates):
    """
    计算指定时间段内的【标准应出勤天数】。

    逻辑修正：
    1. 节假日 (holiday) -> 不算。
    2. 调休 (swap):
       - 如果是物理周末 (Sat/Sun) 被标记为 swap -> 说明是补班 -> 算工作日。
       - 如果是物理工作日 (Mon-Fri) 被标记为 swap -> 说明被调休成休息了 -> 不算。
    3. 普通工作日:
       - 既不是节假日，也不是调休的物理工作日 -> 算工作日。
    """
    start = datetime.strptime(start_date_str, "%Y%m%d")
    end = datetime.strptime(end_date_str, "%Y%m%d")

    count = 0
    curr = start
    while curr <= end:
        date_str = curr.strftime("%Y-%m-%d")

        # 1. 优先级最高：如果是显式的节假日，直接不算
        if date_str in holiday_dates:
            curr += timedelta(days=1)
            continue

        is_phys_weekday = curr.weekday() < 5  # 0-4 是周一至周五
        is_swap = date_str in swap_dates

        if is_swap:
            # === 核心修正逻辑 ===
            # 如果是调休：
            # 只有当它是【物理周末】时，才意味着是"补班" (需要出勤)
            # 如果它是【物理工作日】且被标记为 swap，通常意味着这天调休变假了 (不需要出勤)
            if not is_phys_weekday:
                count += 1
        else:
            # 如果不是调休，且不是节假日：
            # 只要是物理工作日，就需要出勤
            if is_phys_weekday:
                count += 1

        curr += timedelta(days=1)

    return count


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

def statistic_person(name, record_week, class_schedule, travel_dates, leave_dates, holiday_dates, swap_dates):
    """
    Args:
        name: 姓名
        record_week: 考勤原始数据列表
        class_schedule: 课表字典
        travel_dates: 出差日期集合 (set of "YYYY-MM-DD")
        leave_dates: 请假日期集合 (set of "YYYY-MM-DD")
        holiday_dates: 节假日日期集合 (set of "YYYY-MM-DD")
        swap_dates: 调休补班日期集合 (set of "YYYY-MM-DD")
    """
    # --- 配置常量 (分钟) ---
    AM_WINDOW_START = 450  # 07:30
    AM_WINDOW_END = 570  # 09:30
    AM_SPLIT = 810  # 13:30
    PM_WINDOW_START = 810  # 13:30
    PM_WINDOW_END = 870  # 14:30
    PM_SPLIT = 1110  # 18:30
    EVE_CHECKOUT_LIMIT = 1410  # 23:30

    # 1. 初始化结果
    result_person = {'姓名': name}
    total_hours = 0
    missing_count = 0

    # 遍历每一天
    for record_day in record_week:
        checkin_date = record_day['checkin_date']  # "20251001"
        day_str = format_datetime(checkin_date)  # "10-01"

        # 转为 "YYYY-MM-DD" 用于查集合
        current_date_obj = datetime.strptime(str(checkin_date), "%Y%m%d")
        check_date_str = current_date_obj.strftime("%Y-%m-%d")

        # === 核心逻辑1：判断当天“是否应出勤” (考核标准) ===
        is_phys_weekday = current_date_obj.weekday() < 5
        is_swap_workday = check_date_str in swap_dates
        is_holiday = check_date_str in holiday_dates
        is_on_leave = check_date_str in leave_dates
        is_on_travel = check_date_str in travel_dates

        should_attendance_day = False

        # 优先级判断应出勤状态
        if is_holiday:
            should_attendance_day = False
        elif is_swap_workday:
            # 调休逻辑：
            # 物理周末(Sat/Sun) + Swap标记 = 补班 (需要出勤)
            # 物理工作日(Mon-Fri) + Swap标记 = 休息 (不需要出勤)
            should_attendance_day = not is_phys_weekday
        elif is_phys_weekday:
            should_attendance_day = True

        # 如果请假或出差，当天不算“缺勤”考核日，但可能需要算工时
        # 这里逻辑是：如果本该出勤，但请假了，那么 attendance_check 为 False (不计缺勤)
        attendance_check_needed = should_attendance_day and not (is_on_leave or is_on_travel)

        # === 核心逻辑2：不管是否需要出勤，都获取数据并计算 ===
        # 只有这样才能满足“有人周末还来，要记录打卡”的需求

        # 获取物理打卡
        raw_checkin_records = record_day.get('month_day_data', [])
        # 获取课程时间 (注意：generate_class_schedule 已经处理好了逻辑日期映射，直接取 checkin_date 即可)
        person_schedule = class_schedule.get(name, {})
        day_classes = person_schedule.get(checkin_date, [])

        am_points = []
        pm_points = []
        eve_points = []

        # (A) 处理物理打卡
        has_phys_data = False
        for r in raw_checkin_records:
            t_str = format_timestamp(r['checkin_time'])
            t_min = time_to_minutes(t_str)
            if t_min == -1: continue

            has_phys_data = True  # 标记有物理打卡数据
            point = (t_min, 'phys')

            if t_min < AM_SPLIT:
                am_points.append(point)
            elif AM_SPLIT <= t_min < PM_SPLIT:
                pm_points.append(point)
            else:
                eve_points.append(point)

        # (B) 处理课程时间
        for course in day_classes:
            start_min = time_to_minutes(course['start'])
            end_min = time_to_minutes(course['end'])
            if start_min == -1 or end_min == -1: continue

            p_start = (start_min, 'class')
            p_end = (end_min, 'class')

            if start_min < AM_SPLIT:
                am_points.append(p_start)
            elif start_min < PM_SPLIT:
                pm_points.append(p_start)
            else:
                eve_points.append(p_start)

            if end_min < AM_SPLIT:
                am_points.append(p_end)
            elif end_min < PM_SPLIT:
                pm_points.append(p_end)
            else:
                eve_points.append(p_end)

        # === 定义计算函数 (保持不变) ===
        def calculate_session(points, start_min_limit, start_max_limit, end_hard_limit=None):
            if not points: return 0, '-', '-'
            # ... (此处保持你原有的 calculate_session 内部逻辑代码不变) ...
            # 为节省篇幅，假设这里是你原来的 calculate_session 代码内容
            phys_points = sorted([p for p in points if p[1] == 'phys'], key=lambda x: x[0])
            class_points = sorted([p for p in points if p[1] == 'class'], key=lambda x: x[0])

            start_candidates = []
            if phys_points:
                p_start = phys_points[0][0]
                is_phys_valid = True
                if start_min_limit is not None and start_max_limit is not None:
                    if not (start_min_limit <= p_start <= start_max_limit):
                        is_phys_valid = False
                if is_phys_valid:
                    start_candidates.append((p_start, 'phys'))
            if class_points:
                start_candidates.append((class_points[0][0], 'class'))

            if not start_candidates: return 0, '-', '-'
            start_candidates.sort(key=lambda x: x[0])
            valid_start_time, start_source = start_candidates[0]

            all_sorted = sorted(points, key=lambda x: x[0])
            valid_end_candidates = []
            for p_time, p_type in all_sorted:
                if end_hard_limit is not None and p_time > end_hard_limit: continue
                valid_end_candidates.append((p_time, p_type))
            if not valid_end_candidates: return 0, '-', '-'

            valid_end_time = valid_end_candidates[-1][0]
            end_source = valid_end_candidates[-1][1]

            start_str = minutes_to_time_str(valid_start_time) + ("(课)" if start_source == 'class' else "")
            if valid_start_time >= valid_end_time: return 0, start_str, '-'

            duration = (valid_end_time - valid_start_time) / 60.0
            end_label = "(课)" if end_source == 'class' else ""
            end_str = minutes_to_time_str(valid_end_time) + end_label
            return duration, start_str, end_str

        # 分段计算
        eff_am, am_in, am_out = calculate_session(am_points, AM_WINDOW_START, AM_WINDOW_END)
        eff_pm, pm_in, pm_out = calculate_session(pm_points, PM_WINDOW_START, PM_WINDOW_END)
        eff_eve, eve_in, eve_out = calculate_session(eve_points, None, None, end_hard_limit=EVE_CHECKOUT_LIMIT)

        # 累计工时 (无论是否节假日，只要干活了就算工时)
        total_hours += (eff_am + eff_pm + eff_eve)

        # === 核心逻辑3：结果展示处理 ===
        # 需求：如果是节假日/不需要出勤，但有打卡，要显示打卡；如果没有打卡，显示备注。

        display_data = {
            'am_in': am_in, 'am_out': am_out,
            'pm_in': pm_in, 'pm_out': pm_out,
            'eve_in': eve_in, 'eve_out': eve_out
        }

        # 如果当天【没有任何有效打卡/课程计算出数据】，且属于特殊状态，则覆盖显示文本
        # 判断依据：am_in, pm_in, eve_in 都是 '-'
        is_empty_record = (am_in == '-' and pm_in == '-' and eve_in == '-')

        if is_empty_record:
            if is_holiday:
                status_str = '(节假日)'
                display_data = {k: status_str for k in display_data}
            elif is_on_leave:
                status_str = '(请假)'
                display_data = {k: status_str for k in display_data}
            elif is_on_travel:
                status_str = '(出差)'
                display_data = {k: status_str for k in display_data}
            elif not should_attendance_day:
                # 调休休息日或普通周末，且没来
                display_data = {k: '-' for k in display_data}
        else:
            # 有打卡数据！
            # 即使是节假日，这里也会显示计算出的时间，满足你的需求1和2
            pass

        result_person[day_str] = display_data

        # === 核心逻辑4：统计缺勤 ===
        # 只有在 (应该出勤) 且 (没请假/没出差) 的情况下，才校验是否缺勤
        if attendance_check_needed:
            if eff_am == 0: missing_count += 1
            if eff_pm == 0: missing_count += 1

    # 汇总
    total_hours = round(total_hours, 2)
    result_person['实际出勤时长'] = total_hours
    result_person['周期缺勤次数'] = missing_count

    return result_person


####################################################################################################

def statistic(infos, class_schedule, travel_map, leave_map, holiday_dates, swap_dates, exclude_person=None):
    """
    中间层函数，透传 swap_dates 参数
    """
    result = []
    for person_info in infos:
        name = person_info['member_name'].strip()
        if exclude_person and name in exclude_person:
            continue
        try:
            person_travel_dates = travel_map.get(name, set())
            person_leave_dates = leave_map.get(name, set())

            result.append(
                statistic_person(
                    name,
                    person_info['month_days'],
                    class_schedule,
                    person_travel_dates,
                    person_leave_dates,
                    holiday_dates,
                    swap_dates  # <--- 传入到单人统计
                )
            )
        except Exception as e:
            traceback.print_exc()
            print(f"处理 '{person_info['member_name']}' 数据时出错: {e}")
    return result


####################################################################################################

def fetch(conn, cursor, token, req_data):
    """
    入口函数，从数据库获取调休配置并生成 swap_dates 集合
    """
    start_date = req_data['start_date']
    end_date = req_data['end_date']

    start_date_format = datetime.strptime(start_date, "%Y%m%d").date()
    end_date_format = datetime.strptime(end_date, "%Y%m%d").date()

    # 1. 获取课表学期配置
    cursor.execute("""
        SELECT id, start_date, end_date
        FROM semester_class
        WHERE enable = 1
        ORDER BY id DESC LIMIT 1
    """)
    row = cursor.fetchone()
    semester_id = row["id"]
    semester_start = row["start_date"]
    semester_end = row["end_date"]

    cursor.execute("""
        SELECT name, week, slot, type
        FROM semester_class_item
        WHERE semester_class_id = ?
    """, (semester_id,))
    items = [dict(r) for r in cursor.fetchall()]

    # 2. 获取日历例外配置 (调休/节假日)
    # 假设 start_date 为 "20251001"，转为 "2025-10-01" 查库
    q_start = datetime.strptime(start_date, "%Y%m%d").strftime("%Y-%m-%d")
    q_end = datetime.strptime(end_date, "%Y%m%d").strftime("%Y-%m-%d")

    cursor.execute("""
        SELECT date, type, swap_date, description 
        FROM calendar_override 
        WHERE date >= ? AND date <= ?
    """, (q_start, q_end))

    override_rows = cursor.fetchall()

    override_map = {}
    holiday_dates = set()
    swap_dates = set()  # <--- 新增：存储所有调休补班的物理日期 (格式 YYYY-MM-DD)

    for r in override_rows:
        # 将数据库 date (可能是 date 对象或 str) 统一转为 YYYYMMDD (用于排课 key) 和 YYYY-MM-DD (用于统计集合)
        raw_date = r['date']
        if isinstance(raw_date, str):
            dt = datetime.strptime(raw_date, "%Y-%m-%d")
        else:
            dt = datetime(raw_date.year, raw_date.month, raw_date.day)

        k_date = dt.strftime("%Y%m%d")
        fmt_date = dt.strftime("%Y-%m-%d")

        # 构建 map (给排课用)
        val = {"type": r['type']}
        if r['type'] == 'swap' and r['swap_date']:
            # 处理 swap_date
            s_date = r['swap_date']
            if isinstance(s_date, str):
                val['swap_date'] = datetime.strptime(s_date, "%Y-%m-%d")
            else:
                val['swap_date'] = datetime(s_date.year, s_date.month, s_date.day)

        override_map[k_date] = val

        # 构建节假日集合
        if r['type'] == 'holiday':
            holiday_dates.add(fmt_date)

        # 构建调休工作日集合 (新增逻辑)
        if r['type'] == 'swap':
            swap_dates.add(fmt_date)

    # 3. 生成课表 (传入 override_map)
    class_info = generate_class_schedule(
        start_date,
        end_date,
        items,
        semester_start,
        semester_end,
        override_map
    )

    # 4. 获取出差记录
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
        trip_start = datetime.strptime(start_str, '%Y-%m-%d').date()
        trip_end = datetime.strptime(end_str, '%Y-%m-%d').date()
        calc_start = max(trip_start, start_date_format)
        calc_end = min(trip_end, end_date_format)
        days_in_range = 0
        current_date = calc_start
        while current_date <= calc_end:
            travel_map[user_name].add(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)
            days_in_range += 1
        current_total = working_hour.get(user_name, 0)
        working_hour[user_name] = current_total + (avg_working_hours * days_in_range)

    # 5. 获取请假记录
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
        trip_start = datetime.strptime(start_str, '%Y-%m-%d').date()
        trip_end = datetime.strptime(end_str, '%Y-%m-%d').date()
        calc_start = max(trip_start, start_date_format)
        calc_end = min(trip_end, end_date_format)
        current_date = calc_start
        while current_date <= calc_end:
            leave_map[user_name].add(current_date.strftime("%Y-%m-%d"))
            current_date += timedelta(days=1)

    # 6. 获取实验室配置
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

    # 7. 统计数据
    data_list = []
    for toke in token:
        lab = toke['name']
        exclude_person = lab_info.get(lab, [])
        raw_data = fetchdata(start_date, end_date, toke['Authorization'], toke['org_id'], toke['member_id'])

        processed_data = statistic(
            raw_data,
            class_schedule=class_info,
            travel_map=travel_map,
            leave_map=leave_map,
            holiday_dates=holiday_dates,
            swap_dates=swap_dates,  # <--- 核心修改：传入调休工作日集合
            exclude_person=exclude_person
        )
        data_list.extend(processed_data)

    # 8. 后处理
    standard_work_days = calculate_standard_work_days(start_date, end_date, holiday_dates, swap_dates)

    final_list = []
    for person_data in data_list:
        name = person_data['姓名']
        actual_hours = person_data.get('实际出勤时长', 0)
        travel_add_hours = working_hour.get(name, 0)
        final_total_hours = actual_hours + travel_add_hours

        person_data['出差补录时长'] = round(travel_add_hours, 2)
        person_data['最终出勤时长'] = round(final_total_hours, 2)
        person_data['日均考勤时长'] = round(final_total_hours / standard_work_days, 2)

    data_list.sort(key=lambda x: x['最终出勤时长'], reverse=True)

    for index, person_data in enumerate(data_list):
        ordered_data = {'排名': index + 1}
        ordered_data.update(person_data)
        final_list.append(ordered_data)

    return final_list

