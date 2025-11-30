import io
import os
import smtplib
from datetime import datetime, date
from datetime import timedelta
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def create_detail_workbook(data, start_date, end_date):
    wb = openpyxl.Workbook()
    ws = wb.active

    center_align = Alignment(horizontal='center', vertical='center')

    # 只定义一种填充色：淡黄色
    light_yellow_fill = PatternFill(start_color="FFFFE0", end_color="FFFFE0", fill_type="solid")  # LightYellow

    # 定义一个细灰色边框样式
    thin_grey_side = Side(style='thin', color='D3D3D3')
    thin_border = Border(left=thin_grey_side,
                         right=thin_grey_side,
                         top=thin_grey_side,
                         bottom=thin_grey_side)

    dates = []
    current_date = datetime.strptime(start_date, "%Y%m%d")
    end_dt = datetime.strptime(end_date, "%Y%m%d")
    while current_date <= end_dt:
        dates.append(current_date.strftime("%m-%d"))
        current_date += timedelta(days=1)

    static_headers = ["姓名", "应出勤(小时)", "总出勤(小时)", "有效天数", "是否达标"]
    headers = static_headers + dates
    ws.append(headers)
    ws.row_dimensions[1].height = 25
    for cell in ws[1]:
        cell.alignment = center_align
        cell.border = thin_border

    ws.column_dimensions[get_column_letter(1)].width = 12
    ws.column_dimensions[get_column_letter(2)].width = 15
    ws.column_dimensions[get_column_letter(3)].width = 15
    ws.column_dimensions[get_column_letter(4)].width = 12
    ws.column_dimensions[get_column_letter(5)].width = 12
    for i in range(len(dates)):
        col_letter = get_column_letter(len(static_headers) + 1 + i)
        ws.column_dimensions[col_letter].width = 13

    time_slots_info = [('am_in', ''), ('am_out', ''), ('pm_in', ''), ('pm_out', ''), ('eve_in', ''), ('eve_out', '')]

    current_row = 2
    for person_index, person in enumerate(data):
        start_row_for_person = current_row

        static_data = [
            person["姓名"], person["应该出勤(小时)"], person["实际出勤(小时)"],
            person["有效出勤天数"], person["是否达标"]
        ]
        for i, value in enumerate(static_data, start=1):
            ws.cell(row=current_row, column=i, value=value)
            ws.merge_cells(start_row=current_row, start_column=i, end_row=current_row + 5, end_column=i)

        for col_offset, day in enumerate(dates):
            current_col = len(static_headers) + 1 + col_offset
            day_times = person.get(day, {})
            for row_offset, (key, _) in enumerate(time_slots_info):
                time_value = day_times.get(key, '-')
                ws.cell(row=current_row + row_offset, column=current_col, value=f"{time_value}")

        # 遍历这个人的6行数据
        for row_index in range(start_row_for_person, start_row_for_person + 6):
            ws.row_dimensions[row_index].height = 22.5
            # 遍历这一行的所有列
            for col_index in range(1, len(headers) + 1):
                cell = ws.cell(row=row_index, column=col_index)
                # 对所有单元格应用对齐和边框
                cell.alignment = center_align
                cell.border = thin_border

                # person_index 为 0, 2, 4... 时，填充黄色
                # person_index 为 1, 3, 5... 时，不执行填充，保留默认白色
                if person_index % 2 == 0:
                    cell.fill = light_yellow_fill

        current_row += 6

    return wb


def create_rank_workbook(data, start_date, end_date, num, workday_count):
    def calculate_duration(start_str, end_str):
        """根据开始和结束时间字符串（HH:MM），计算持续时间（小时）。"""
        if start_str == '-' or end_str == '-':
            return 0
        clean_start_str = start_str.split(' ')[0]
        clean_end_str = end_str.split(' ')[0]
        dummy_date = date(2023, 1, 1)
        try:
            start_time = datetime.strptime(clean_start_str, '%H:%M').time()
            end_time = datetime.strptime(clean_end_str, '%H:%M').time()
        except ValueError:
            return 0
        start_dt = datetime.combine(dummy_date, start_time)
        end_dt = datetime.combine(dummy_date, end_time)
        if end_dt < start_dt:
            return 0
        duration = end_dt - start_dt
        return duration.total_seconds() / 3600

    start_date_obj = datetime.strptime(start_date, '%Y%m%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y%m%d').date()

    year_from_start_date = start_date_obj.year
    processed_data = []

    for employee in data:
        total_hours = 0
        days_worked_actual = 0

        for date_key, attendance in employee.items():
            if isinstance(attendance, dict) and 'am_in' in attendance:
                try:
                    current_date_str = f"{year_from_start_date}-{date_key}"
                    current_date = datetime.strptime(current_date_str, '%Y-%m-%d').date()
                except ValueError:
                    continue

                if start_date_obj <= current_date <= end_date_obj:
                    daily_hours = calculate_duration(attendance.get('am_in', '-'), attendance.get('am_out', '-')) + \
                                  calculate_duration(attendance.get('pm_in', '-'), attendance.get('pm_out', '-')) + \
                                  calculate_duration(attendance.get('eve_in', '-'), attendance.get('eve_out', '-'))

                    if daily_hours > 0:
                        total_hours += daily_hours
                        days_worked_actual += 1

        average_daily_hours = (total_hours / workday_count) if workday_count > 0 else 0

        processed_data.append({
            '姓名': employee['姓名'],
            '总出勤(小时)': round(total_hours, 2),
            '有效出勤天数': days_worked_actual,
            '日均出勤(小时)': round(average_daily_hours, 2)
        })

    sorted_data = sorted(processed_data, key=lambda x: x['总出勤(小时)'], reverse=True)

    wb = Workbook()
    ws = wb.active

    headers = ['排名', '姓名', '总出勤(小时)', '有效出勤天数', '日均出勤(小时)']
    ws.append(headers)

    center_align = Alignment(horizontal='center', vertical='center')
    yellow_fill = PatternFill(start_color="FFFFFF00", end_color="FFFFFF00", fill_type="solid")

    column_widths = {'A': 8, 'B': 15, 'C': 18, 'D': 18, 'E': 18}
    for col, width in column_widths.items():
        ws.column_dimensions[col].width = width

    ws.row_dimensions[1].height = 25
    for cell in ws[1]:
        cell.alignment = center_align

    for i, employee_data in enumerate(sorted_data, start=1):
        row_to_write = [
            i,
            employee_data['姓名'],
            employee_data['总出勤(小时)'],
            employee_data['有效出勤天数'],
            employee_data['日均出勤(小时)']
        ]
        ws.append(row_to_write)

        current_row_num = ws.max_row
        ws.row_dimensions[current_row_num].height = 22.5

        for cell in ws[current_row_num]:
            cell.alignment = center_align
            if i <= num:
                cell.fill = yellow_fill

    return wb


def send_email_with_attachments(recipient_list, subject, body, attachments):
    sender_email = 'xmulab309@163.com'
    sender_password = 'YSRQQMBRTDNEZNZI'
    smtp_server = 'smtp.163.com'
    smtp_port = 465

    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = ', '.join(recipient_list)
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    for attachment in attachments:
        filename = attachment['filename']
        content = attachment['content']

        part = MIMEApplication(content)
        part.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(part)

    # --- 发送邮件 ---
    try:
        client = smtplib.SMTP_SSL(smtp_server, smtp_port)
        client.login(sender_email, sender_password)
        client.sendmail(sender_email, recipient_list, msg.as_string())
        client.quit()
        return True
    except smtplib.SMTPException as e:
        raise e


def excel(conn, cursor, data, req_data):
    start_date = req_data['start_date']
    end_date = req_data['end_date']

    detail_wb = create_detail_workbook(data, start_date, end_date)
    rank_wb = create_rank_workbook(data, start_date, end_date, 5, req_data['attendance_days'])

    detail_virtual_workbook = io.BytesIO()
    detail_wb.save(detail_virtual_workbook)
    detail_virtual_workbook.seek(0)

    rank_virtual_workbook = io.BytesIO()
    rank_wb.save(rank_virtual_workbook)
    rank_virtual_workbook.seek(0)

    cursor.execute("SELECT email FROM attendance_account WHERE id = ?", (req_data["account_id"],))
    account_row = cursor.fetchone()
    email_list = dict(account_row)['email']
    email_list = [email.strip() for email in email_list.split(',') if email.strip()]

    email_subject = f"考勤报表 ({start_date} 至 {end_date})"
    email_body = f"您好，\n\n附件是您申请的从 {start_date} 到 {end_date} 的考勤数据报表。"

    attachments_to_send = [
        {
            'filename': f"考勤明细-{start_date}-{end_date}.xlsx",
            'content': detail_virtual_workbook.read()
        },
        {
            'filename': f"考勤排名-{start_date}-{end_date}.xlsx",
            'content': rank_virtual_workbook.read()
        }
    ]

    send_email_with_attachments(
        recipient_list=email_list,
        subject=email_subject,
        body=email_body,
        attachments=attachments_to_send
    )

