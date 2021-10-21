from selenium import webdriver
import urllib
import operator
import sqlite3
import time
# DB 생성 (오토 커밋)
conn = sqlite3.connect("test.db", isolation_level=None)
# 커서 획득
c = conn.cursor()
# 테이블 생성 (데이터 타입은 TEST, NUMERIC, INTEGER, REAL, BLOB 등)
c.execute("CREATE TABLE IF NOT EXISTS keyword_table(name text PRIMARY KEY, k1 text, k1_v int, k2 text, k2_v int, k3 text, k3_v int, k4 text, k4_v int,k5 text, k5_v int)")


# DataBase에서 찾고자 하는 상품명을 입력 후 결과 출력

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
driver2 = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
driver3 = webdriver.Chrome(executable_path="chromedriver.exe", options=chrome_options)
while(True):
    query = input("검색할 단어 : ")
    param1 = (query,)
    c.execute('SELECT * FROM keyword_table WHERE name=?', param1)
    in_db = c.fetchone()
    # print(in_db)
    if(in_db == None):
        print("검색중입니다. 잠시만 기다려주세요.")
        url_query = urllib.parse.quote(query)
        driver.get("https://search.shopping.naver.com/search/all?query="+url_query+"&cat_id=&frm=NVSHATC") 
        raw_data = []
        cal_data = {}
        sql_Data = []
        count = 0
        for class_name in driver.find_elements_by_class_name('basicList_link__1MaTN'):
            if(count == 5):
                break
            #print(class_name.get_attribute('href'))
            driver2.get(class_name.get_attribute('href'))
            temp_url = class_name.get_attribute('href')
            # print(temp_url)
            # print(temp_url.find('shopping.naver.com'))
            if(temp_url.find('shopping.naver.com') != -1):
                c_name = driver2.find_element_by_class_name('productList_title__uCZ0P')
                driver3.get(c_name.get_attribute('href'))
                x = driver3.find_element_by_xpath("//meta[@name='keywords']")
                raw_data.append(x.get_attribute('content').split(','))
                print(x.get_attribute('content'))
            else :
                x = driver2.find_element_by_xpath("//meta[@name='keywords']")
                raw_data.append(x.get_attribute('content').split(','))
                print(x.get_attribute('content'))
            count += 1
        # print(data)
        
        for i, keywords in enumerate(raw_data):
            for keyword in keywords:
                if keyword in cal_data:
                    cal_data[keyword] = cal_data[keyword] + (10 - i)
                else :
                    cal_data[keyword] = 10 - i
        # print(cal_data)
        sorted_data = sorted(cal_data.items(), key=operator.itemgetter(1), reverse=True)
        
        for key, value in sorted_data:
            if key == '':
                continue
            else :
                sql_Data.append([key, value])
        
        DB_input = "(" + "\'" + query + "\'" + ", "
        for i in range(5):
            DB_input = DB_input + "\'" + sql_Data[i][0] + "\'" + ", " + str(sql_Data[i][1])
            if(i == 4):
                DB_input = DB_input + ")"
            else:
                DB_input = DB_input + ", "
        
        # DB_input 예시 ('살균제', '살균', 95, '사용이편리한', 92, '살균세척제', 91, '소독', 88, '소독제', 85)
        
        # DataBase에 크롤링으로 추출한 데이터 삽입
        c.execute("INSERT INTO keyword_table VALUES" + DB_input)
        print(DB_input)
    else:
        print(in_db)

    print("검색하시려면 아무키나 눌러주세요")
    x = input("X키를 누르면 종료됩니다.")
    if(x == 'X'):
        break
