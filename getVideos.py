from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


driver = webdriver.Chrome('.\\chromedriver.exe')
driver.maximize_window()

channels = ["UCsXVk37bltHxD1rDPwtNM8Q", "UC-lHJZR3Gqxm24_Vd_AJ5Yw", "UCONd1SNf3_QqjzjCVsURNuA", "UC5nc_ZtjKW1htCVZVRxlQAQ", "UC-kIKjS3gUFvsi4YoxveiWA",
            "UC2-_WWPT_124iN6jiym4fOw", "UC_GQ4mac4oN3wl1UdbFuTEA"]

for channel in channels:
    baseUrl = "https://www.youtube.com/channel/" + channel
    driver.get(baseUrl)
    print("\n--------------------------\n")
    print(channel)
    print("\n--------------------------\n")
    # clica em VIDEOS
    driver.find_element_by_xpath(
        "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/app-toolbar/div/div/paper-tabs/div/div/paper-tab[2]/div").click()
    file = open(".\\canais_files" + channel, "w+")
    alreadyVisited = []
    elements = []
    while(True):
        prevelements = elements
        height = driver.execute_script("return document.body.scrollHeight")
        time.sleep(1)
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        print(height)
        elements = driver.find_elements_by_xpath("//a[@id='thumbnail']")
        for element in elements:
            try:
                if element not in alreadyVisited:
                    alreadyVisited.append(element)
                    link = element.get_attribute("href")
                    print(link)
                    if link != None:
                        file.write(link)
                        file.write("\n")
            except:
                continue
        if len(elements) == len(prevelements):
            break




