from selenium import webdriver  #從library中引入webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os #可以用來取得路徑位置
import pymysql.cursors

from datetime import date
today = date.today()
print(today)

from datetime import datetime
now = datetime.now()
created_at = now.strftime("%Y-%m-%d, %H:%M:%S")
print("date and time:",created_at)

connection = pymysql.connect(host='localhost',
                             user='user', 
                             password='password', 
                             db='new_media', 
                             cursorclass=pymysql.cursors.DictCursor)

options = Options() #初始化瀏覽器的選項別

options.add_argument('--headless') #設定選項為 “headless” 和無 gpu 模式
# options.add_argument('--disable-gpu')
options.experimental_options["prefs"] = {'profile.default_content_settings' : {"images": 2},
                                         'profile.managed_default_content_settings' : {"images": 2}}

chromedriver_path = os.getcwd() + "/chromedriver-linux64"

driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)


try:
    with connection.cursor() as cursor:
        for i in range(1, 5):
            # driver.get('https://www.inside.com.tw/category/headline?page='+str(i))
            driver.get('https://www.inside.com.tw/?page='+str(i))
            sourceCode = BeautifulSoup(driver.page_source, features="html.parser")
            mainSection = sourceCode.select('div.post_list')[0]
            post_items = mainSection.select('div.post_list_item') 
            for post_item in post_items: 
                # category = post_item.select('a.post_category.badge')[0].text
                title = post_item.select('h3.post_title')[0].text
                # author = post_item.select('span.post_author')[0].text
                date = post_item.select('li.post_date')[0].text.strip()
                converted_date_str = date.replace("/", "-")
                tags = post_item.select('a.hero_slide_tag')
                tags_string = ''
                for tag in tags:
                    tags_string += tag.text + ', '

                # 只寫入今日資料
                # print(converted_date_str)
                if(converted_date_str == str(today)):

                    print(title)
                    print(converted_date_str)
                    print(tags_string)
                    
                    sql = "INSERT INTO media_posts (title, date, tags, source, created_at) VALUES (%s, %s, %s, %s, %s)"
                    val = (title, converted_date_str, tags_string, 'inside', created_at)
                    
                    cursor.execute(sql, val)
                    connection.commit()

            
    connection.close()
    driver.close()
except Exception as e:
    print(e)
    connection.close()
    driver.close()
