import time
from bs4 import BeautifulSoup
import requests_html
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import yaml
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import log
import logging
import traceback
import re
logger = logging.getLogger('robot')
class robot:
    def __init__(self, acc, pw, driver):
        self.acc = acc
        self.pw = pw
        self.driver = driver
    def login(self):
        while True:
            try:
                self.driver.get('https://www.maersk.com/portaluser/login')
                WebDriverWait(self.driver, 30, 0.5).until(EC.title_is('Login - Maersk Identity and Access Management Portal'))
                cookies = self.driver.find_element_by_css_selector('button[aria-label="Allow all"]')
                if cookies:
                    cookies.click()
                self.driver.find_element_by_css_selector('input[id="usernameInput"]').send_keys(self.acc)
                time.sleep(1)
                self.driver.find_element_by_css_selector('input[id="passwordInput"]').send_keys(self.pw)
                time.sleep(1)
                self.driver.find_element_by_css_selector('button[class="mt-4 button button--primary"]').click()
                # 判斷15分鐘才能登入
                html = requests_html.HTML(html=self.driver.page_source)
                data = html.find('div[class="notification__text"] > span.p')
                if data and data[0].text == 'Please wait 15 minutes before you log in again':
                    logger.warning('等待15分鐘重登')
                    time.sleep(900)
                    continue
                return self.driver
            except Exception as e:
                logger.critical('\n' + traceback.format_exc())
                time.sleep(3)
                continue
    def instantPrice(self,data):
        while True:
            try:
                #新網址
                self.driver.get('https://www.maersk.com/instantPrice/')
                WebDriverWait(self.driver, 30, 0.5).until(EC.title_is('Combined Pricing Journey'))
                logger.info(f"機器人回報任務:開始輸入搜尋資料>出港[{data['select_from']}]，入港[{data['select_to']}]")
                #select_from
                for key in data['select_from']:
                    self.driver.find_element_by_css_selector('div[class="searchFormOrigin"] input[placeholder="Enter city name"]').send_keys(key)
                    time.sleep(0.1)
                time.sleep(1)
                self.driver.find_element_by_css_selector('div[class="typeahead__suggestions typeahead__suggestions--open"] li').click()
                time.sleep(1)

                #select_to
                for key in data['select_to']:
                    self.driver.find_element_by_css_selector('div[class="searchFormDestination"] input[placeholder="Enter city name"]').send_keys(key)
                    time.sleep(0.1)
                time.sleep(1)
                self.driver.find_element_by_css_selector('div[class="typeahead__suggestions typeahead__suggestions--open"] li').click()
                time.sleep(1)

                #Commodity
                self.driver.find_element_by_css_selector('input[placeholder="Enter Commodity"]').send_keys(data['Commodity'])
                time.sleep(1)
                self.driver.find_element_by_css_selector('div[class="typeahead__suggestions typeahead__suggestions--open"] li').click()

                #Container_type
                self.driver.find_element_by_css_selector('input[placeholder="Select container type"]').send_keys(data['Container_type'])
                time.sleep(1)
                self.driver.find_element_by_css_selector('div[class="typeahead__suggestions typeahead__suggestions--open"] li').click()

                #select_date
                self.driver.find_element_by_css_selector('input[placeholder="Select Date"]').click()
                time.sleep(1)
                self.driver.find_element_by_css_selector(f'tr > td[title="{data["select_date"]}"]').click()
                time.sleep(1)

                #search
                self.driver.find_element_by_css_selector('button[class="button button--primary"]').click()
                #time.sleep(4)
                #確定頁面加載完成
                WebDriverWait(self.driver, 30, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME,'available-rates')))
                return self.driver
            except Exception as e:
                logger.critical('\n' + traceback.format_exc())
                time.sleep(3)
                continue
    def departure_dates(self, lens):
        content = []
        switch = False #詳細資料是否開啓
        while True:
            try:
                for i in range(1, lens+1):
                    resp = {}
                    total = 0 #金額總和
                    currency = '' #幣別
                    self.driver.find_element_by_css_selector(f'div.available-rates section div.combined-slide.desktop div[aria-hidden="false"]:nth-child({i})').click()
                    html = requests_html.HTML(html=self.driver.page_source)
                    date = html.find('div.available-rates section div.combined-slide.desktop div[aria-hidden="false"] div.slide-inside--date > div')[i-1].text
                    # 判斷有無下拉視窗
                    if not html.find('div[class="text-icon toggle desktop"]'):
                        logger.info(f'機器人回報任務:已處理第{i}/{lens}筆資料, 船期:{date}, 總價格:無')
                        continue
                    if not switch:
                        self.driver.find_element_by_css_selector('div.text-icon.toggle.desktop > span').click()
                        html = requests_html.HTML(html=self.driver.page_source)
                        switch = True
                    # d = html.find('section.schedule-info > div > dl > dd')[0].text
                    # date = re.search('(?P<long_date>\d+ \w+).+', d).groupdict()['long_date']
                    moneys = [data.text for data in html.find('section.rate-details-card.flex--row.wrap td[data-test="freight--charge-container-wise"]')]
                    for money in moneys:
                        total += float(re.search('(?P<currency>\w+) (?P<money>.+)', money).groupdict()['money'].replace(',',''))
                        if not currency:
                            currency = re.search('(?P<currency>\w+) (?P<money>.+)', money).groupdict()['currency']
                    resp['Departure'] = date
                    resp['Ocean Freight'] = f'{currency}{total:.2f}'
                    content.append(resp)
                    logger.info(f'機器人回報任務:已處理第{i}/{lens}筆資料, 船期:{date}, 總價格:{currency}{total:.2f}')
                return content
            except Exception as e:
                logger.critical('\n' + traceback.format_exc())
                time.sleep(3)
                continue

    def times(self,days:int = 0):
        while True:
            try:
                times = (datetime.datetime.now() + datetime.timedelta(days=3+days)).strftime("%d %b %Y")
                return times
            except Exception as e:
                logger.info(str(e))
                time.sleep(3)
                continue

    def email(self, email, filename):
        content = MIMEMultipart()
        content['subject'] = '自動查運費'#郵件標題
        content['from'] = 'mailkill2000@gmail.com'#寄件者
        content['to'] = email#收件者
        content.attach(MIMEText("運費內容如附件")) #郵件內容
        files = filename #檔案位置
        part_attach = MIMEApplication(open(files,'rb').read()) #讀取附件
        part_attach.add_header('Content-Disposition','attachment',filename=files.split('\\')[-1]) #生成附件
        content.attach(part_attach) #新增附件
        with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
            try:
                smtp.ehlo()
                smtp.starttls()
                smtp.login('mailkill2000@gmail.com','cskqkpghgjhtltzj')
                smtp.send_message(content)
                logger.info(f'機器人回報寄件任務成功，寄送位置:{email}')
                return True
            except Exception as e:
                logger.info(f"機器人回報寄件任務失敗，錯誤訊息為:{e}")
                return False

def read_file():
    #讀取檔案
    file = open('config.txt', 'r', encoding='utf-8')
    f = file.read()
    data = f.encode('utf-8').decode('utf-8-sig')
    return eval(data)

def read_yaml():
    try:
        file = open('config.yaml','r',encoding='utf-8')
        data = yaml.load(file.read(), yaml.SafeLoader)
        return data
    except Exception as e:
        logger.info(e)
        return '無設定檔或設定檔格式有誤'