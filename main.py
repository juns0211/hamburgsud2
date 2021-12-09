import requests_html
from robot import robot, read_yaml
import time
import datetime
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import log
import logging
import traceback
from pathlib import Path
logger = logging.getLogger('robot')

def main():
    #to_excel = 準備傳出去的excel檔格式
    to_excel = {'POL(From)':[],'POD(To)':[],'ETD(departure)':[],'Ocean Freight':[]}
    except_count = 0
    path = str(Path('chromedriver.exe').absolute())
    #讀取檔案
    cf = read_yaml()
    if isinstance(cf,str):
        return cf
    while True:
        try:
            #選擇是否開啓視窗
            if cf['windows']:
                options = webdriver.ChromeOptions()
                options.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志
                driver = webdriver.Chrome(path, chrome_options=options)
                driver.set_page_load_timeout(cf['timeout'])
            else:
                options = webdriver.ChromeOptions()
                options.add_argument('headless')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志
                driver = webdriver.Chrome(path, chrome_options=options)
                driver.set_page_load_timeout(cf['timeout'])
            driver.implicitly_wait(10) #隱性等待時間
            content = robot(cf['acc'], cf['pw'], driver)
            for i,j in zip(cf['From'], cf['To']):
                while True:
                    if not cf['login']:
                        logger.info('機器人回報任務:開始進行登入')
                        content.login()
                        # 確認來到此頁,最多等N秒,每0.5秒檢查一次
                        WebDriverWait(content.driver, 1800, 0.5).until(EC.title_is('Maersk :: Hub'))
                        logger.info('機器人回報任務:登入成功')
                        cf['login'] = True
                        time.sleep(1.5) #防止被鎖
                    oldtimes = content.times()
                    cf['data']['select_date'] = oldtimes
                    cf['data']['select_from'] = i
                    cf['data']['select_to'] = j
                    rep = content.instantPrice(cf['data'])
                    logger.info(f"機器人回報任務:輸入搜尋資料完成>出港[{cf['data']['select_from']}]，入港[{cf['data']['select_to']}]")
                    break
                html = requests_html.HTML(html=rep.page_source)
                departure_dates = html.find('div.available-rates section div.combined-slide.desktop div[aria-hidden="false"]')
                if not departure_dates:
                    logger.info(f'出港[{i}], 入港[{j}], 查無資料')
                    continue
                result = content.departure_dates(len(departure_dates))
                for i in result:
                    to_excel['POL(From)'] += [cf['data']['select_from']]
                    to_excel['POD(To)'] += [cf['data']['select_to']]
                    to_excel['ETD(departure)'] += [i['Departure']]
                    to_excel['Ocean Freight'] += [i['Ocean Freight']]
            if to_excel.get('POL(From)'):
                excel = pd.DataFrame(to_excel)
                file_path_time = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
                writer = pd.ExcelWriter(f"運費報告{file_path_time}.xlsx", engine='xlsxwriter')
                excel.to_excel(writer,sheet_name='運費報告',index=False)
                writer.save()
                file_path = f'{os.getcwd()}\\運費報告{file_path_time}.xlsx'
                logger.info('機器人回報任務:己存取EXCEL成功')
                logger.info(f'機器人回報任務:檔案路徑:{file_path}')
                content.email(cf['email'], file_path)
                logger.info('機器人回報任務:任務結束')
                start_time = datetime.datetime.now() + datetime.timedelta(minutes=cf['robot_timeout'])
                logger.info(f"關閉延時共:{cf['robot_timeout'] * 60}秒, 預計:{start_time.strftime('%Y-%m-%d %H:%M:%S')}關閉網頁")
                time.sleep(cf['robot_timeout'] * 60) #轉換為秒
                return
            else:
                logger.info('任務結束:查無價格')
                return
        except TimeoutException as e:
            logger.critical('\n' + traceback.format_exc())
            content.driver.close()
            cf['login'] = False
            except_count += 1
            time.sleep(5)
            if except_count > 5:
                logger.warning(f'機器人發生錯誤,已連續錯誤{except_count}次，程式將停止')
                return '機器人發生錯誤,程式停止'
            else:
                logger.warning(f'機器人發生錯誤,進行第{except_count}次重試')
                continue
        except (Exception, NoSuchElementException) as e:
            logger.critical('\n' + traceback.format_exc())
            content.driver.close()
            cf['login'] = False
            except_count += 1
            time.sleep(5)
            if except_count > 5:
                logger.warning(f'機器人發生錯誤,已連續錯誤{except_count}次，程式將停止')
                return '機器人發生錯誤,程式停止'
            else:
                logger.warning(f'機器人發生錯誤,進行第{except_count}次重試')
                continue

if __name__ == "__main__":
    rep = main()
    if isinstance(rep, str):
        input('請按ENTER鍵結束程式')