# automating the login to Upstox terminal
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


browser = webdriver.Chrome('/Users/shayakroy/anaconda3/lib/python3.7/chromedriver')

login_id = '214062'
password1 = 'Shayak@28feb'
password2 = '1986'

browser.get('https://pro.upstox.com/')

delay = 2 # seconds

browser.implicitly_wait(10)
browser.find_element_by_xpath("/html/body/main/main/header/div[1]/div[2]/div[7]").click()
browser.implicitly_wait(10)
# user name
browser.find_element_by_xpath("//*[@id='login-fields-container']/div/div[1]/div[2]/div[1]/input").send_keys(login_id + Keys.ENTER)
# password
browser.find_element_by_xpath("//*[@id='login-fields-container']/div/div[1]/div[2]/div[2]/input").send_keys(password1 + Keys.ENTER)
browser.implicitly_wait(10)
browser.find_element_by_xpath("//*[@id='login-fields-container']/div/div[2]/div/div[3]/input").send_keys(password2 + Keys.ENTER)

browser.quit()



