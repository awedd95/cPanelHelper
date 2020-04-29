from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
browser = Firefox()
browser.get('https://demo.cpanel.net:2083/')
usernameInput = browser.find_element_by_id("user")
passwordInput =browser.find_element_by_id("pass")
submitLogin = browser.find_element_by_id("login_submit")


usernameInput.send_keys('democom')
passwordInput.send_keys('DemoCoA5620')
submitLogin.click()

myElem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'icon-addon_domains')))
browser.find_element_by_id("icon-addon_domains").click()

newDomain = browser.find_element_by_id("domain")
subDomain = browser.find_element_by_id("subdomain")
submitDomain = browser.find_element_by_id("submit_domain")
newDomain.send_keys("Smallpp.com")
subDomain.click()
submitDomain.click()
