import json
import sqlite3
import time
import platform

from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver

from views.constants.constants import *
from views.enums.enums import *


def token(conn, cursor, _id, req_data):
    cursor.execute("SELECT * FROM attendance_account WHERE id = ?", (req_data["account_id"],))
    account = dict(cursor.fetchone())

    # 先去查缓存
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        "SELECT * FROM attendance_token WHERE account_id = ? AND date = ?",
        (account["id"], today)
    )
    row = cursor.fetchone()
    if row:
        return json.loads(dict(row).get('token'))

    res = []

    # 配置 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    # 在无头模式下运行，服务器环境通常没有图形界面
    chrome_options.add_argument('--headless')
    # 禁用 GPU 加速，在某些服务器环境中是必需的
    chrome_options.add_argument('--disable-gpu')
    # 解决 DevToolsActivePort 文件不存在的报错
    chrome_options.add_argument('--no-sandbox')
    # 禁用 /dev/shm 共享内存，防止资源限制问题
    chrome_options.add_argument('--disable-dev-shm-usage')

    # 创建一个 WebDriver 实例
    if platform.system() == 'Windows':
        driver = webdriver.Chrome(service=Service('chromedriver.exe'), options=chrome_options)
    else:
        driver = webdriver.Chrome(options=chrome_options)

    try:
        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("进入主页面", datetime.now(), _id))
        conn.commit()

        driver.get("https://www.delicloud.com/")
        driver.maximize_window()
        time.sleep(1)

        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("进入管理后台", datetime.now(), _id))
        conn.commit()

        # 点击“管理后台”
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "a.nav-item-manage[href='https://v2-web.delicloud.com/login']"))
        ).click()
        time.sleep(1)

        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("登陆账号", datetime.now(), _id))
        conn.commit()

        # 输入账号
        mobile_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'mobile'))
        )
        mobile_input.send_keys(account['mobile'])

        # 输入密码
        password_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'password'))
        )
        password_input.send_keys(account['password'])

        # 点击登录
        login_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[span[text()='登 录']]"))
        )
        login_button.click()

        # 点击获取验证码
        get_code_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//div[text()='获取验证码']"))
        )
        get_code_button.click()

        # 更新状态为需要验证码
        cursor.execute("""
            UPDATE attendance_statistics
            SET status=?, update_date = ?
            WHERE id = ?
        """, (StatisticsEnum.NEED_CAPTCHA.code, datetime.now(), _id))
        conn.commit()

        # 开始轮询查询验证码是否已经拿到
        captcha = ''
        for i in range(0, 60 * 2):
            cursor.execute("SELECT * FROM attendance_statistics WHERE id = ?", (_id,))
            row = dict(cursor.fetchone())
            captcha = row.get('captcha')
            if captcha:
                break
            time.sleep(1)
        if not captcha:
            raise RuntimeError("获取验证码超时")

        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("输入验证码", datetime.now(), _id))
        conn.commit()

        # 输入验证码
        verify_code_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='请输入验证码']"))
        )
        verify_code_input.send_keys(captcha)

        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("登录账号", datetime.now(), _id))
        conn.commit()

        # 登录
        confirm_button = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//button[span[text()='确 定']]"))
        )
        confirm_button.click()

        # 等待加载
        time.sleep(5)

        cursor.execute("""
            UPDATE attendance_statistics
            SET message=?, update_date=?
            WHERE id=?
        """, ("登录成功", datetime.now(), _id))
        conn.commit()

        # 抓取所有组织项
        org_items = driver.find_elements(By.XPATH,
                                         '//*[@id="root"]/div[2]/div[3]/ul//div[contains(@class,"org_item__KY9pv")]')
        # 如果没有找到“所有组织项”，说明这个账号只管理了一个组织
        if len(org_items) == 0:
            org_items = [0]

        for i in range(len(org_items)):
            if len(org_items) > 1:
                org_items = driver.find_elements(By.XPATH,
                                                 '//*[@id="root"]/div[2]/div[3]/ul//div[contains(@class,"org_item__KY9pv")]')
                org = org_items[i]
                org.click()
                time.sleep(1)

            # 名字
            org_name = driver.find_element(By.CLASS_NAME, 'layout_hd_name__SILWV').text

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据", datetime.now(), _id))
            conn.commit()

            try:
                skip_button = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//div[contains(@class,'ant-modal-body')]//span[contains(text(),'跳 过')]")))
                driver.execute_script("arguments[0].click();", skip_button)
                time.sleep(1)
            except:
                pass

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据：综合签到", datetime.now(), _id))
            conn.commit()

            checkin_link = driver.find_element(By.XPATH,
                                               "//a[contains(@class,'dashboard_col__sfMxv') and span[contains(text(),'综合签到')]]")
            driver.execute_script("arguments[0].click();", checkin_link)
            WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
            new_tab = driver.window_handles[-1]
            driver.switch_to.window(new_tab)
            time.sleep(1)

            try:
                skip_button = WebDriverWait(driver, 2).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//div[contains(@class,'ant-modal-body')]//span[contains(text(),'跳 过')]")))
                driver.execute_script("arguments[0].click();", skip_button)
                time.sleep(1)
            except:
                pass

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据：考勤页面", datetime.now(), _id))
            conn.commit()

            # 点击”考勤“
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//li[normalize-space()="考勤"]'))
            ).click()
            time.sleep(1)

            # 检查是否存在考勤提示区域，有的话要把他关掉
            try:
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//div[contains(@class, 'slick-slide') and contains(@class, 'slick-active')]")))
                time.sleep(1)

                cursor.execute("""
                    UPDATE attendance_statistics
                    SET message=?, update_date=?
                    WHERE id=?
                """, (f"获取{org_name}数据：关闭提示", datetime.now(), _id))
                conn.commit()

                while True:
                    # 如果出现“我知道了”按钮，则点击并退出循环
                    try:
                        know_btn = driver.find_element(
                            By.XPATH, "//button[contains(@class,'ant-btn-primary')]//span[text()='我知道了']"
                        )
                        driver.execute_script("arguments[0].click();", know_btn)
                        break
                    except Exception:
                        pass
                    # 否则点击右箭头
                    try:
                        right_arrow = driver.find_element(By.CLASS_NAME, "rule_arrow_right__2586S")
                        driver.execute_script("arguments[0].click();", right_arrow)
                        time.sleep(1)
                    except Exception:
                        break
                time.sleep(1)

                try:
                    finish_btn = driver.find_element(By.XPATH,
                                                     "//button[contains(@class,'ant-btn-primary')]//span[text()='完 成']")
                    driver.execute_script("arguments[0].click();", finish_btn)
                except Exception:
                    pass
                time.sleep(1)
            except Exception:
                pass

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据：考勤数据", datetime.now(), _id))
            conn.commit()

            # 点击“考勤数据”
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(@class,'ant-menu-submenu-title')]//span[contains(text(),'考勤数据')]"))
            ).click()
            time.sleep(1)

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据：月度汇总", datetime.now(), _id))
            conn.commit()

            # 点击“月度汇总”
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(@class,'ant-menu-item')]/span[contains(text(),'月度汇总')]"))
            ).click()
            time.sleep(1)

            cursor.execute("""
                UPDATE attendance_statistics
                SET message=?, update_date=?
                WHERE id=?
            """, (f"获取{org_name}数据：抓取网络请求", datetime.now(), _id))
            conn.commit()

            # 抓取请求
            time.sleep(5)
            for request in reversed(driver.requests):
                if request.url.endswith('findMonthReport'):
                    auth = request.headers.get("authorization")
                    org_id = request.headers.get("org_id")
                    member_id = request.headers.get("member_id")
                    res.append({"name": org_name, "Authorization": auth, "org_id": org_id, "member_id": member_id})
                    break

            if len(org_items) > 1:
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                driver.back()
                time.sleep(1)
    except Exception as e:
        raise e
    finally:
        driver.quit()

    # 清空今天之前的缓存
    cursor.execute(
        "DELETE FROM attendance_token WHERE date < ?",
        (today,)
    )
    # 写入缓存
    cursor.execute("""
    INSERT INTO attendance_token (account_id, date, token, create_date, update_date)
    VALUES (?, ?, ?, ?, ?)
    """, (account["id"], today, json.dumps(res, ensure_ascii=False), datetime.now(), datetime.now()))
    conn.commit()

    return res
