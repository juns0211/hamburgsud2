import logging,os
import datetime

logger = logging.getLogger('hamburgsud')
logger.setLevel(logging.DEBUG)
handler =  logging.FileHandler(os.getcwd() + f"\\{datetime.datetime.now().strftime('%Y-%m-%d')}的記錄檔.log", encoding='utf-8')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

#控制台輸出
console = logging.StreamHandler()
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
console.setLevel(logging.DEBUG)