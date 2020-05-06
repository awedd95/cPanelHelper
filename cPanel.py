from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import functools
import time

class cPanel():
    def init(self):
        global browser
        browser = Firefox()
        browser.implicitly_wait(10)
        cPanelSite = 'https://cp1.cloudable.net.au:2083'
        browser.get(cPanelSite)

    def wait(self):
        WebDriverWait(browser, 10)

    def login(self):
#       self.browser.get(cPanelSite)
        configFile = open('config.txt','r')
        config = []
        for line in configFile:
            config.append(line)
        self.userName = config[0]
        self.password = config[1]
        usernameInput = browser.find_element_by_id("user")
        passwordInput = browser.find_element_by_id("pass")
        submitLogin = browser.find_element_by_id("login_submit")
        usernameInput.send_keys(self.userName)
        passwordInput.send_keys(self.password)
        submitLogin.click()

    def goToAddDomains(self):
        myElem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'icon-addon_domains')))
        browser.find_element_by_id("icon-addon_domains").click()
    
    @functools.lru_cache(maxsize=128)
    def getElements(self):
        existing = []
        table =  browser.find_element_by_xpath("//*[@id='subdomaintbl']")
        for row in table.find_elements(By.TAG_NAME, "tr"):
            for td in row.find_elements(By.TAG_NAME, "td[data-title='Subdomain']"):
                existing.append(td.text)
        return existing

    def checkSubdomains(self, site, existing):
        subDomain = browser.find_element_by_id("subdomain")
        print(existing)
        if site in existing:
            print("I'm checking")
            site += "i"
            subDomain.send_keys("i")
            return self.checkSubdomains(site, existing)
        else:
            return 'ok'

    def addDomain(self, site):
        browser.find_element_by_xpath("//*[@id='DEFAULT-page-itemsperpage']/option[text()='1000']").click()
        self.wait()
        newDomain = browser.find_element_by_id("domain")
        subDomain = browser.find_element_by_id("subdomain")
        submitDomain = browser.find_element_by_id("submit_domain")
        newDomain.send_keys(site)
        check = str(site.split(".")[0])
        exists = self.getElements()
        subDomain.click()
        self.wait()
        proceed = ''
        proceed = self.checkSubdomains(check, exists)
        print(proceed)
        if proceed == "ok":
            submitDomain.click()
    
    def goBack(self):
        self.wait()
        backButton = browser.find_element_by_id("lnkReturn")
        backButton.click()

    def goToDNS(self):
        myElem = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'icon-addon_domains')))
        browser.find_element_by_id("icon-zone_editor").click()

    def addDNSRecord(self, site):
        filterBox = browser.find_element_by_id('filterList_input')
        filterBox.send_keys(site)
        browser.find_elements(By.Css_Selector,"html body#zone_editor.cpanel.yui-skin-sam.cpanel_body div#wrap div#content.container-fluid div.body-content div#viewContent.section div#tableShowHideContainer div#tableContainer.domain-selection-view table#table.table.table-striped.responsive-table tbody tr td.action-buttons button:nth-child(3)").click()
def main():
    page = cPanel()
    sites = []
    file = open("addresses.txt", "r")
    for line in file:
        sites.append(line)
    print('Please choose an option:')
    print('1 - Add addon domains to cPanel')
    print('2 - Add DNS records')
    option = input("Type the number for the option:")
    if(option == '1'):
        page.init()
        page.login()
        page.goToAddDomains()
        for site in sites:
            page.addDomain(site)
            time.sleep(1)
            page.goBack()
        print("done: Added " + str(len(sites)) + " addon domains.")
    
    if(option == '2'):
        page.init()
        page.login()
        page.goToDNS()
        page.addDNSRecord("akin.asia")

if __name__ == "__main__":
    main()
