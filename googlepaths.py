from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from time import sleep


class Chrome:
    def __init__(self):
        option = Options()
        option.add_experimental_option("detach", True)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)

    def find_work(self, src):
        return self.find(src, "Käthe-Kollwitz-Straße 1, 04109 Leipzig")

    def find_htwk(self, src):
        return self.find(src, "HTWK Leipzig")

    def find(self, src, dest):
        self.driver.switch_to.new_window('tab')
        url = f"https://www.google.com/maps/dir/{src}/{dest}"
        self.driver.get(url)
        elem = self.driver.find_elements(By.TAG_NAME, "button")
        for i in elem:
            if i.accessible_name == "Alle akzeptieren":
                i.click()
                break
        self.driver.find_element(By.CSS_SELECTOR, "div[data-travel_mode='3']").click()
        sleep(1)
        dirs = self.driver.find_elements(By.CSS_SELECTOR, "div[aria-label$='min']")
        mins = []
        for dir in dirs:
            mins.append(int(dir.text.split(" ")[0]))
        self.close_tab()
        return min(mins)


    def close_tab(self):
        ActionChains(self.driver) \
            .key_down(Keys.CONTROL) \
            .send_keys("w") \
            .key_up(Keys.CONTROL) \
            .perform()


    def open_markets(self, src):
        self.driver.switch_to.new_window('tab')
        url = f"https://www.google.com/maps/search/{src}/"
        self.driver.get(url)
        elem = self.driver.find_elements(By.TAG_NAME, "button")
        for i in elem:
            if i.accessible_name == "Alle akzeptieren":
                i.click()
                break
        self.driver.find_element(By.CSS_SELECTOR, "div[aria-label^='Suche']").click()
        self.driver.find_element(By.ID, "searchboxinput").send_keys(f"Supermärkte near {src}")
        self.driver.find_element(By.CSS_SELECTOR, "button[aria-label^='Suche']").click()

