import logging

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep


class Chrome:
    def __init__(self, detach=False):
        self.detach = detach
        option = Options()
        option.add_experimental_option("detach", detach)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    def find_work(self, src):
        return self.find(src, "Käthe-Kollwitz-Straße 1, 04109 Leipzig")

    def find_htwk(self, src):
        return self.find(src, "HTWK Leipzig")
    def quit(self):
        self.driver.quit()

    def check_internet(self, full_address, zip, tries=0):
        address, number = tuple(full_address.split("."))
        address = (address + ".").replace("_", " ").replace("Straße", "Str").replace("straße", "str")
        number = number.strip()
        url = "https://www.check24.de/dsl/input2/"

        self.driver.get(url)
        cookies = self.driver.find_elements(By.CLASS_NAME, "c24-cookie-consent-button")
        for i in cookies:
            if i.accessible_name == "Akzeptieren":
                i.click()
                break
        sleep(1)
        self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='PLZ oder Ort']").send_keys(zip)
        radios = self.driver.find_elements(By.CSS_SELECTOR, "label[for^='radio']")
        for r in radios:
            if r.text == "Nein":
                r.click()
                break
        self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Straße']").send_keys(address)
        self.driver.find_element(By.CSS_SELECTOR, "input[placeholder='Nr.']").send_keys(number)
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        sleep(11)
        try:
            self.driver.find_element(By.CSS_SELECTOR, "div[data-value='downstream']").click()
        except Exception as e:
            if tries >= 3:
                logging.error("cannot submit? ", e)
                return -1
            elif tries == 1:
                return Chrome(self.detach).check_internet(full_address.replace("  Str", "Str").replace("  str", "str"), zip, tries + 1)
            elif tries == 2:
                return Chrome(self.detach).check_internet(full_address.replace(" ", ""), zip, tries + 1)
            else:
                return Chrome(self.detach).check_internet(full_address.replace("Str", " Str").replace("str", " str"), zip, tries+1)
        sleep(10)
        internet = int(self.driver.find_elements(By.CLASS_NAME, "tko-flatrate-value")[0].text.split(" ")[0].replace(".", ""))
        print("internet:", internet)
        return internet

    def find(self, src, dest):
        self.driver.switch_to.new_window('tab')
        url = f"https://www.google.com/maps/dir/{src}, Leipzig/{dest}"
        self.driver.get(url)
        elem = self.driver.find_elements(By.TAG_NAME, "button")
        for i in elem:
            if i.accessible_name == "Alle akzeptieren":
                i.click()
                break
        self.driver.find_element(By.CSS_SELECTOR, "div[data-travel_mode='3']").click()
        sleep(4)
        dirs = self.driver.find_elements(By.CSS_SELECTOR, "div[aria-label$='min']")
        if not dirs: sleep(5)
        mins = []
        for dir in dirs:
            print("Google Time Label:", dir.text)
            if ("h" in dir.text[:10]):
                print("more than 1 hour")
                mins.append(65)
                continue
            time = dir.text.split(" min")[0]
            print("Time:", time)
            mins.append(int(time))
        print("mins:", mins)
        self.close_tab()
        if not mins: return -1
        print(min(mins))
        return min(mins)


    def close_tab(self):
        ActionChains(self.driver) \
            .key_down(Keys.CONTROL) \
            .send_keys("w") \
            .key_up(Keys.CONTROL) \
            .perform()


    def open_markets(self, src, plz):
        self.driver.switch_to.new_window('tab')
        url = f"https://www.google.com/maps/search/{src}, {plz}/"
        self.driver.get(url)
        elem = self.driver.find_elements(By.TAG_NAME, "button")
        for i in elem:
            if i.accessible_name == "Alle akzeptieren":
                i.click()
                break
        self.driver.find_element(By.CSS_SELECTOR, "div[aria-label^='Suche']").click()
        self.driver.find_element(By.ID, "searchboxinput").send_keys(f"Supermärkte near {src}, {plz}")
        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label^='Suche']").click()