from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import functools
import time
import tkinter as tk
import json

class cPanel():
    
    with open("usable.json") as json_file:
        data = json.load(json_file)

    def init(self):
        global browser
        browser = Firefox()
        browser.implicitly_wait(10)
        cPanelSite = 'https://cp1.cloudable.net.au:2083'
        browser.get(cPanelSite)

    def wait(self):
        WebDriverWait(browser, 10)

    def login(self):
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
 
    def printRecords(self, item):
            data = {
                    'IPAddress' : '',
                    'Exchange' : '',
                    'Priority' : 0,
                    'text' : '',
                    'domain' : ''
            }
            for record in item["records"]:
                recordType = list(record.keys())[0]
                if recordType == '1':
                    data['IPAddress'] = item["records"][item["records"].index(record)][recordType]
                if recordType == '15':
                    data['Exchange'] = item["records"][item["records"].index(record)][recordType][0]['Exchange']
                    data['Priority'] = item["records"][item["records"].index(record)][recordType][1]['Priority']
                if recordType == '16':
                    data['text'] = item["records"][item["records"].index(record)][recordType]
            data['domain'] = item["domain"]
            return(data)

    def recordType(self):
        if type == "1":
            return "A"
        if type == "28":
            return "AAAA"
        if type == "15":
            return "MX"
        if type == "5":
            return "CNAME"
        if type == "16":
            return "TXT"


    def addDNSRecord(self):
        self.wait()
        filterBox = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID,'filterList_input')))
        filterBox = browser.find_element_by_id("filterList_input")
        for item in self.data:
            data = self.printRecords(item)
            filterBox.send_keys(data['domain'])
            print(filterBox.get_attribute('value')
#           if data['domain'] in filterBox.text:
#               manage = browser.find_element_by_css_selector("tbody tr td.action-buttons button:nth-child(5)")
#               manage.click()
            self.wait()
            addRecordButton = browser.find_element_by_id("search_add_record_btn")
            recordName = browser.find_element_by_id("recordName")
            recordType = browser.find_element_by_id("recordType")
#           recordValue = browser.find_element_by_class("record_subelement subelement_input")
            self.wait()
#           addRecordButton.click()
#           recordName.send_keys("test")
#           recordValue.send_keys("test")
#           recordType.select_by_value("AAAA")

        
    
class Gui(tk.Frame):
    sites = []
    file = open("addresses.txt", "r")
    for line in file:
        sites.append(line)
    page = cPanel()

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def startBrowser(self):
        self.page.init()
        self.page.login()

    def addDomainsGui(self):
        self.startBrowser()
        self.page.goToAddDomains()
        for site in self.sites: 
            self.page.addDomain(site)
            time.sleep(1)
            self.page.goBack()

    def addDNSGui(self):
        self.startBrowser()
        self.page.goToDNS() 
        #for site in self.sites: 
        self.page.addDNSRecord()
    def testRecords(self):
        self.page.printRecords()

    def create_widgets(self):
        self.addDomains = tk.Button(self, text="Add Addon Domains", command=self.addDomainsGui)
        self.addDomains.pack(side="top")
        
        self.addRecords = tk.Button(self, text="Add DNS Records", command=self.addDNSGui)
        self.addRecords.pack(side="top")
        
        self.testRecords = tk.Button(self, text="Test DNS Records", command=self.testRecords)
        self.testRecords.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",command=self.master.destroy)
        self.quit.pack(side="bottom")

if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(master=root)
    app.mainloop()
