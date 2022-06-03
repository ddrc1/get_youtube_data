from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


driver = webdriver.Chrome('./chromedriver.exe')
driver.maximize_window()

# IDs de canais previamente escolhidos
channels = config.CHANNELS['right'] + config.CHANNELS['left']

for channel in channels:
    baseUrl = "https://www.youtube.com/channel/" + channel
    driver.get(baseUrl)
    print("\n--------------------------\n")
    print(channel)
    print("\n--------------------------\n")

    # clica em VIDEOS
    driver.find_element_by_xpath(
        "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[3]/ytd-c4-tabbed-header-renderer/app-header-layout/div/app-header/div[2]/app-toolbar/div/div/paper-tabs/div/div/paper-tab[2]/div").click()
    file = open("./video_links/" + channel + ".txt", "w+")
    alreadyVisited = []
    elements = []

    while(True):
        prevelements = elements
        height = driver.execute_script("return document.body.scrollHeight")
        print(height)

        time.sleep(1)
        driver.find_element_by_tag_name('body').send_keys(Keys.END)
        
        # Adquire a lista de vídeos visíveis
        elements = driver.find_elements_by_xpath("//a[@id='thumbnail']")
        for element in elements:
            try:
                if element not in alreadyVisited:
                    alreadyVisited.append(element)
                    
                    #adquire o id do video para salvar no arquivo referente ao canal
                    link = element.get_attribute("href")
                    print(link)
                    if link != None:
                        file.write(link)
                        file.write("\n")
            except:
                continue
        
        # Se não for possível dar mais scroll, quer dizer que não existem mais videos no canal e o loop se encerra
        if len(elements) == len(prevelements):
            break
