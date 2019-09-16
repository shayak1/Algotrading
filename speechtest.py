import webbrowser
import speech_recognition as sr
from selenium import  webdriver
from selenium.webdriver.common.keys import Keys


r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say something!")
    audio = r.listen(source)

try:
    text = r.recognize_google(audio)
    print("You said: {}".format(text))
except:
    print("Sorry cant recognize")

query = text

browser = webdriver.Chrome('/Users/shayakroy/anaconda3/lib/python3.7/chromedriver')
browser.get('https://www.google.com/')
browser.find_element_by_xpath("//*[@id='tsf']/div[2]/div/div[1]/div/div[1]/input").send_keys(query + Keys.ENTER)

