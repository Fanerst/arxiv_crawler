from selenium import webdriver
import time
import os.path
import datetime


def get_date_today():
    day = datetime.date.today().strftime('%Y%m%d')
    return day 


def webshot(url, saveImgName):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    js_height = "return document.body.clientHeight"
    picname = saveImgName
    link = url 
    # driver.get(link)
    try:
        driver.get(link)
        k = 1
        height = driver.execute_script(js_height)
        while True:
            if k * 500 < height:
                js_move = "window.scrollTo(0,{})".format(k * 500)
                print(js_move)
                driver.execute_script(js_move)
                time.sleep(0.2)
                height = driver.execute_script(js_height)
                k += 1
            else:
                break
        scroll_width = driver.execute_script('return document.body.parentNode.scrollWidth')
        scroll_height = driver.execute_script('return document.body.parentNode.scrollHeight')
        driver.set_window_size(scroll_width, scroll_height)
        driver.get_screenshot_as_file(picname + ".png")
        
        print("Process {} get one pic !!!".format(os.getpid()))
        time.sleep(0.1)
    except Exception as e:
        print(picname, e)
 
 
if __name__ == '__main__':
    t = time.time()
    webshot('https://scholar.google.com/citations?user=ZDEkIDsAAAAJ&hl=en', f'snapshot/{get_date_today()}')
    print("Done in {:.2f} seconds.".format(float(time.time() - t)))