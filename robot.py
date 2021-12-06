import time
from bs4 import BeautifulSoup
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import yaml
from logger import logger
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
class request_robot:
    def __init__(self, acc, pw):
        self.acc = acc
        self.pw = pw

    def javax(self):
        while True:
            headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                'cache-control': 'max-age=0',
                #'cookie: JSESSIONID=227d210ee959029efb98f3bec976; NSC_JOnsxwg1eakpv1we5smnfuddwl54heT=ffffffff09c0ef0b45525d5f4f58455e445a4a423660; AKA_A2=A; ak_bmsc=3CBAEAA8DC8A880BDC2644DCA2A6FAB668549663A265000028C2356038404F0B~plqnjicod4ue63/zmSjpy8gmQBAJ/rUYqSmXVAWaDRiO9X/shg91KV+EQMd20LM5Tc4PGdMp9AC5IQgEFOB2Eptpxzq2gkc7vxs9OaPRpGLSww9MlYIEWWou0OW3elBhvjEJDY3CCKbEKlslcd90JU+MsF42OGynUxBBr5xsq3JDAqqJqc5S05/7U8rwvS+r7k0RWcBnJrjkWokbHAr82IAyqiMib6Jsxkf1tetbYFQZ+Bn876tgrOn3Khqxd0dQLzlFEjCAtSsGeDUoeHASTH16NbOZst3dF3PVSz0WZ6/bv+/qxQIl8sqrzpBcjXE0HQ; __cmpcc=1; __cmpcvcu6055=__s23_s24__; __cmpcpcu6055=____; _ga=GA1.2.1231995605.1614135864; _gid=GA1.2.619816091.1614135864',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
            }
            rep = requests.get('https://www.hamburgsud-line.com/linerportal/pages/hsdg/login.xhtml?lang=en',headers=headers,timeout=20)
            if rep.status_code == 200:
                soup = BeautifulSoup(rep.text,'lxml')
                javax_faces_ViewState = soup.find('input',{'name':'javax.faces.ViewState'}).get('value')
                javax_faces_source = soup.find('div',{'id':'login'}).find('script').get('id')
                loginForm = soup.find('div',{'id':'login'}).find('form').get('id')
                data = {
                    'javax.faces.partial.ajax': 'true',
                    'javax.faces.source':javax_faces_source,
                    'javax.faces.partial.execute':'@all',
                    javax_faces_source:javax_faces_source,
                    'clientTimeZone':'Asia/Taipei',
                    loginForm:loginForm,
                    f'{loginForm}:loginNameOrEmail':'',
                    f'{loginForm}:password':'',
                    'javax.faces.ViewState':javax_faces_ViewState,
                }
                return data
            else:
                continue

class robot:
    def __init__(self, acc, pw, driver):
        self.acc = acc
        self.pw = pw
        self.driver = driver
    def login(self):
        while True:
            try:
                # self.driver.get('https://www.hamburgsud-line.com/liner/en/liner_services/ecommerce/login/login_stage.html')
                # WebDriverWait(self.driver, 30, 0.5).until(EC.title_is('Login | Hamburg Süd'))
                self.driver.get('https://www.hamburgsud-line.com/linerportal/pages/hsdg/login.xhtml')
                WebDriverWait(self.driver, 30, 0.5).until(EC.title_is('Liner Portal Login'))
                name = self.driver.find_element_by_css_selector('div > div > div > div > input.ui-inputfield.ui-inputtext.ui-widget.ui-state-default.ui-corner-all')
                name.send_keys(self.acc)
                password = self.driver.find_element_by_css_selector('div > div > div > div > input.ui-inputfield.ui-password.ui-widget.ui-state-default.ui-corner-all')
                password.send_keys(self.pw)
                self.driver.find_element_by_css_selector('div > div > div > div > button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-icon-right.epButton').click()
                return self.driver
            except Exception as e:
                logger.warning(str(e))
                time.sleep(3)
                continue
    def new_booking(self,data):
        while True:
            try:
                #新網址
                self.driver.get('https://www.hamburgsud-line.com/linerportal/pages/hsdg/secured/bookingRequest.xhtml?lang=en')
                soup = BeautifulSoup(self.driver.page_source,'lxml')
                if soup.find('title').text == 'Booking Request':
                    logger.info(f"機器人回報任務:開始輸入搜尋資料>出港[{data['sf']}]，入港[{data['st']}]")
                else:
                    return False
                #sf
                self.driver.find_element_by_css_selector('input[class="ui-autocomplete-input ui-inputfield ui-widget ui-state-default ui-corner-all"]').send_keys(data['sf'])
                time.sleep(0.5)
                self.driver.find_element_by_css_selector('tr[class="ui-autocomplete-item ui-autocomplete-row ui-widget-content ui-corner-all ui-state-highlight"]').click()
                #st
                self.driver.find_element_by_css_selector('span[class="ui-autocomplete toUnLocationAjaxStatus"] > input[class="ui-autocomplete-input ui-inputfield ui-widget ui-state-default ui-corner-all"]').send_keys(data['st'])
                time.sleep(0.5)
                self.driver.find_element_by_css_selector('tr[class="ui-autocomplete-item ui-autocomplete-row ui-widget-content ui-corner-all ui-state-highlight"]').click()
                #sd
                self.driver.find_element_by_css_selector('span[class="ui-calendar hasdatepicker"] > input[class="ui-inputfield ui-widget ui-state-default ui-corner-all hasDatepicker"]').send_keys(data['sd'])
                time.sleep(0.5)
                #cc
                self.driver.find_element_by_css_selector('div.commodityContainerColumn > div.ui-selectonemenu.ui-widget.ui-state-default.ui-corner-all > label').click()
                time.sleep(0.5)
                self.driver.find_element_by_css_selector('div.ui-input-overlay > div.ui-selectonemenu-filter-container > input').send_keys(data['cc'])
                time.sleep(0.5)
                self.driver.find_element_by_css_selector(f'li[data-label="{data["cc"]}"]').click()
                #ct
                self.driver.find_element_by_css_selector('div.container-row-even > div.ui-g.ui-fluid.ui-g-nopad > div:nth-child(2) > div.ui-selectonemenu.ui-widget.ui-state-default.ui-corner-all > div.ui-selectonemenu-trigger.ui-state-default.ui-corner-right').click()
                time.sleep(0.5)
                soup = BeautifulSoup(self.driver.page_source,'lxml')
                ids = [i.get('id') for i in soup.find_all('div',{'class':'ui-input-overlay'})]
                self.driver.find_element_by_css_selector(f'div[id="{ids[3]}"] > div.ui-selectonemenu-filter-container > input').send_keys(data['ct'])
                time.sleep(0.5)
                self.driver.find_element_by_css_selector(f'li[data-label="{data["ct"]}"]').click()
                #cq
                ids = [i.find('input').get('id') for i in soup.find_all('span',{'class':'ui-inputnumber ui-widget'})]
                self.driver.find_element_by_css_selector(f'input[id="{ids[0]}"]').send_keys(data['cq'])
                time.sleep(0.5)
                #cw
                self.driver.find_element_by_css_selector(f'input[id="{ids[1]}"]').send_keys(data['cw'])
                time.sleep(0.5)
                #cu
                rep = soup.find('div',{'class':'container-row-even'}).find('div')
                for i in rep.find_all('div'):
                    if i.find('label') == None:
                        continue
                    if i.find('label').text == 'UoM*':
                        ids = i.find('label',{'class':'ui-corner-all'}).get('id')
                self.driver.find_element_by_css_selector(f'label[id="{ids}"]').click()
                time.sleep(0.5)
                self.driver.find_element_by_css_selector(f'li[data-label="{data["cu"]}"]').click()
                #continue
                time.sleep(0.5)
                for i in soup.find_all('button',{'class':'epButton'}):
                    for j in i.find_all('span'):
                        if j.text == 'Continue':
                            next_id = i.get('id')
                self.driver.find_element_by_css_selector(f'button[id="{next_id}"]').click()
                return self.driver
            except Exception as e:
                #logger.info(str(e))
                time.sleep(3)
                continue

    def later(self):
        while True:
            try:
                self.driver.find_elements_by_css_selector('div.ui-g-2.ui-md-2.ui-xl-2 > button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-text-icon-left.epButton')[-1].click()
                return self.driver
            except Exception as e:
                #logger.info(str(e))
                time.sleep(3)
                continue
    def click(self,data_ri):
        while True:
            try:
                self.driver.find_element_by_css_selector(f'a[id="{data_ri}"]').click()
                return self.driver
            except Exception as e:
                #logger.info(str(e))
                time.sleep(3)
                continue
    def close(self):
        while True:
            try:
                self.driver.find_element_by_css_selector('div.ui-g-12.ui-md-12.ui-lg-3.ui-xl-3 > button').click()
                return self.driver
            except Exception as e:
                #logger.info(str(e))
                time.sleep(3)
                continue
    def times(self,days:int = 0):
        while True:
            try:
                times = (datetime.datetime.now() + datetime.timedelta(days=5+days)).strftime("%d-%b-%Y")
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
        data = yaml.load(file.read(),yaml.SafeLoader)
        return data
    except Exception as e:
        logger.info(e)
        return '無設定檔或設定檔格式有誤'