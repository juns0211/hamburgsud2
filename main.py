#import config as cf
from robot import robot, read_yaml
import time
import datetime
import json
from bs4 import BeautifulSoup
import re
import pandas as pd
import xlsxwriter.exceptions
import os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from logger import logger

def main():
    #to_excel = 準備傳出去的excel檔格式
    to_excel = {'POL(From)':[],'POD(To)':[],'ETD(departure)':[],'Ocean Freight':[]}
    except_count = 0
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
                driver = webdriver.Chrome(chrome_options=options)
                driver.set_page_load_timeout(cf['timeout'])
            else:
                option=webdriver.ChromeOptions()
                option.add_argument('headless')
                options.add_experimental_option('excludeSwitches', ['enable-logging'])#禁止打印日志
                driver = webdriver.Chrome(chrome_options=option)
                driver.set_page_load_timeout(cf['timeout'])
            driver.implicitly_wait(30) #隱性等待時間
            for i,j in zip(cf['From'], cf['To']):
                error = ''
                out = 0
                counts = 0
                while True:
                    content = robot(cf['acc'], cf['pw'], driver)
                    if not cf['login']:
                        logger.info('機器人回報任務:開始進行登入')
                        content.login()
                        # 確認來到此頁,最多等30秒,每0.5秒檢查一次
                        locator = (By.LINK_TEXT, 'New Booking')
                        WebDriverWait(content.driver, 60, 1).until(EC.presence_of_all_elements_located(locator))
                        #WebDriverWait(content.driver, 30, 0.5).until(EC.title_is('Global container shipping with a personal touch | Hamburg Süd'))
                        logger.info('機器人回報任務:登入成功')
                        cf['login'] = True
                        time.sleep(1.5) #防止被鎖
                    oldtimes = content.times()
                    cf['data']['sd'] = oldtimes
                    cf['data']['sf'] = i
                    cf['data']['st'] = j
                    rep = content.new_booking(cf['data'])
                    if rep == False:
                        continue
                    logger.info(f"機器人回報任務:輸入搜尋資料完成>出港[{cf['data']['sf']}]，入港[{cf['data']['st']}]")
                    break
                time.sleep(4)
                soup = BeautifulSoup(rep.page_source, 'lxml')
                try: #判斷是否有錯誤文字
                    error = soup.find_all('div',{'class':'ui-accordion-content ui-helper-reset ui-widget-content'})[-1].find('div').find_all('span')[-1].text
                    if 'Schedule information currently not available. Please proceed without a schedule.' in error:
                        print(f'本次查詢:{i}=>{j},平台回應:{error},將跳過本次查詢')
                        continue
                except Exception as e:
                    #print(e)
                    pass
                times = content.times(days=14)
                times = datetime.datetime.strptime(times + ' 23:59:59', '%d-%b-%Y %H:%M:%S')
                time.sleep(1) #防止被鎖
                while True:
                    locator = (By.CLASS_NAME, 'ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-icon-left.epButton')
                    WebDriverWait(content.driver, 30, 0.5).until(EC.presence_of_all_elements_located(locator))
                    rep = content.later()
                    # 確認later點擊完成,最多等30秒,每0.5秒檢查一次
                    locator = (By.CLASS_NAME,'ui-accordion.ui-widget.ui-helper-reset.ui-hidden-container')
                    WebDriverWait(content.driver, 30, 0.5).until(EC.presence_of_all_elements_located(locator))
                    soup = BeautifulSoup(rep.page_source,'lxml')
                    soup1 = soup.find_all('tr',{'class':'ui-widget-content ui-datatable-even'})
                    for i in soup1:
                        for j in i.find('td').find_all('span'):
                            if j.get('id') == None:
                                continue
                            if 'departureDate' in j.get('id'):
                                #logger.info(j.text.lower())
                                datatimes = datetime.datetime.strptime(j.text.lower(),'%d-%b-%Y %H:%M')
                                if datatimes > times:
                                    out += 1
                                    break
                        if out:
                            break                   
                    else:
                        logger.info(f'機器人回報任務:查詢日{oldtimes}，最後查詢日已達{datatimes}，未達14day+，繼續往下搜尋')
                    # 已查詢至最後(later不能點擊)
                    if soup.find('button',{'class':'ui-button ui-widget ui-state-default ui-corner-all ui-button-text-icon-left epButton'}).get('disabled'):
                        logger.info(f'機器人回報任務:已達最後一頁，停止往下搜尋')
                        break
                    if out:
                        logger.info(f'機器人回報任務:查詢日{oldtimes}，最後查詢日已達{datatimes}，已達14day+，停止往下搜尋')
                        break
                    time.sleep(3) #防止被鎖
                #尋找是否有價錢欄位 
                soup2 = soup.find_all('table',{'class':'ui-panelgrid ui-widget ui-noborder spotPriceSelectionPanelgrid'})
                data_ri = [i.find('tbody').find('td',{'class':'ui-panelgrid-cell spotPriceBookingSelectionColumn1'}).find('a').get('id') for i in soup2]
                #data_ri = [i.get('data-ri') for i in soup1 if 'Charges' in i.text.split('\n')[-1]]
                if data_ri: #有價錢欄位
                    logger.info(f"機器人回報任務:共有{len(data_ri)}筆價格")
                    #logger.info(data_ri)
                    for column in data_ri:
                        rep = content.click(column)
                        time.sleep(1)
                        soup = BeautifulSoup(rep.page_source,'lxml')
                        soup1 = soup.find('tbody',{'id':f"{column.rsplit('j_idt',1)[0] + 'schedules-table_data'}"}).find_all('td')[0].find_all('span')
                        soup2 = soup.find('div',{'id':f'{column.rsplit("j_idt",1)[0] + "spotpriceRates"}'}).find_all('tr',{'class':'ui-widget-content ui-datatable-even'})
                        #money, currency = soup.find('div',{'id':f'{column.rsplit("j_idt",1)[0] + "spotpriceRates"}'}).find_all('tr',{'class':'ui-widget-content ui-datatable-even'})[-1].find_all('td')[-1].text.split(' ')
                        #print(money, currency)
                        for i in soup1:
                            try:
                                if 'departureDate' in i.get('id'):
                                    departure = i.text.rsplit('-',1)[0]
                                    break
                            except Exception as e:
                                print(e)
                                continue
                        else:
                            logger.warning('補捉金額視窗欄位異動')
                            logger.warning(soup1)
                            return '補捉金額視窗欄位異動'

                        for i in soup2:
                            try:
                                if i.find_all('td')[0].text == 'OCEAN FREIGHT':
                                    money, currency = i.find_all('td')[-1].text.split(' ')
                                    break
                            except Exception as e:
                                print(e)
                                continue
                        else:
                            logger.warning('補捉金額視窗欄位異動')
                            logger.warning(soup2)
                            return '補捉金額視窗欄位異動'

                        #content.close()
                        to_excel['POL(From)'] += [cf['data']['sf']]
                        to_excel['POD(To)'] += [cf['data']['st']]
                        to_excel['ETD(departure)'] += [departure]
                        to_excel['Ocean Freight'] += [currency+money]
                        counts += 1
                        logger.info(f'機器人回報任務:已處理第{counts}/{len(data_ri)}筆價格')
                        time.sleep(1) #防止被鎖
                else:
                    logger.info('機器人回報任務:查無價格')
            if to_excel.get('POL(From)'):
                excel = pd.DataFrame(to_excel)
                file_path_time = datetime.datetime.now().strftime('%Y-%m-%d %H%M%S')
                writer = pd.ExcelWriter(f"運費報告{file_path_time}.xlsx", engine='xlsxwriter')
                excel.to_excel(writer,sheet_name='運費報告',index=False)
                writer.save()
                file_path = f'{os.getcwd()}\\運費報告{file_path_time}.xlsx'
                logger.info('機器人回報任務:己存取EXCEL成功')
                logger.info(f'機器人回報任務:檔案路徑:{file_path}')
                email = content.email(cf['email'], file_path)
                logger.info('機器人回報任務:任務結束')
                return email
            else:
                logger.info('任務結束:查無價格')
                return
        except TimeoutException as e:
            logger.warning(str(e).replace('\n','') + '等待發生連線逾時(Timeout)')
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
            logger.warning(e)
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