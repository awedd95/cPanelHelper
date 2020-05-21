from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import functools
import time
from selenium.webdriver.support.ui import Select
import tkinter as tk
import json

class cPanel():
    
    with open("converted.json") as json_file:
        data = json.load(json_file)

    def init(self):
        global browser
        options = Options()
        options.headless = True
        browser = Firefox(options=options)
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

    def remove(self, node):
        time.sleep(1)
        node.find_element_by_css_selector("tbody tr td.action-buttons button:nth-child(2)").click()
        browser.find_element_by_id("modalContinueBtn").click()
        time.sleep(3)

    def clearOld(self):
        print("Started clearing")
        Types = ['CNAME', 'MX', 'A']
        table =  browser.find_element_by_xpath("//*[@id='table']")
        rows = table.find_elements(By.TAG_NAME, "tr")
        td = {}
        time.sleep(1)
        for row in rows:
            item = row.find_elements(By.TAG_NAME, "td[data-title='Type']")
            if item !=[]:
                if item[0].text != "TXT":
                    td[rows.index(row)] = item[0].text
        print(table, rows, td)
        if len(set(td.values()).intersection(Types))>0:
            Test = td.popitem()
            if Test[1] in Types:
                print("removing " + Test[1])
                self.remove(rows[Test[0]])
                time.sleep(1)
                done = self.clearOld()
                return done
        if len(set(td.values()).intersection(Types)) == 0:
            print("Finished removing records")
            return True
   
    def addNewRecords(self, item):
        cleared = False
        print("Clearing defaults")
        cleared = self.clearOld()
        itemRecords = self.data[item] 
        while not cleared:
            time.sleep(1)    
        addRecordButton = browser.find_element_by_id("search_add_record_btn")
        for key in itemRecords:
            if "IPAddress" in key:
                print("Adding" + itemRecords["IPAddress"])
                addRecordButton.click()
                submitRecord = browser.find_element_by_id("inline_add_record_button")
                typeDropDown = Select(browser.find_element_by_id("recordType"))

                browser.find_element_by_id("recordName").send_keys("www")
                browser.find_element_by_id("record_a_address").send_keys(itemRecords["IPAddress"])
                submitRecord.click()
                time.sleep(1)

            if "Exchange" in key:
                for mx in itemRecords["Exchange"]:
                    time.sleep(2)
                    addRecordButton.click()
                    print("clicked")
                    time.sleep(2)
                    submitRecord = browser.find_element_by_id("inline_add_record_button")
                    typeDropDown = Select(browser.find_element_by_id("recordType"))
                    print("Adding " + mx)
                    typeDropDown.select_by_value('MX')
                    browser.find_element_by_id("record_priority_mx").send_keys(itemRecords["Preference"][itemRecords["Exchange"].index(mx)])
                    browser.find_element_by_id("record_exchanger").send_keys(mx)
                    submitRecord.click()
                    time.sleep(1)
                    
            if "text" in key:
                for txt in itemRecords["text"]:
                    time.sleep(2)
                    addRecordButton.click()
                    time.sleep(2)
                    submitRecord = browser.find_element_by_id("inline_add_record_button")
                    typeDropDown = Select(browser.find_element_by_id("recordType"))
                    print("Adding " + txt)
                    typeDropDown.select_by_value('TXT')
                    browser.find_element_by_id("recordName").send_keys(item)
                    browser.find_element_by_id("record_txtdata").send_keys(itemRecords["text"][itemRecords["text"].index(txt)])
                    submitRecord.click()
                    time.sleep(1)

        browser.execute_script("window.history.go(-1)")
        print("we made it")

    def addDNSRecord(self):
        self.wait()
        for item in self.data:
            filterBox = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID,'filterList_input')))
            filterBox = browser.find_element_by_id("filterList_input")
            filterBox.send_keys(item)
            time.sleep(0.5)
            if item in filterBox.get_attribute('value'):
                manage = browser.find_element_by_css_selector("tbody tr td.action-buttons button:nth-child(5)")
                addressExists = (manage != None)
                if addressExists:
                    manage.click()
                    time.sleep(2)  
                    print("Adding " + item)
                    self.addNewRecords(item)
                else:
                    print(item + " not found")
                    with open('toBeAdded.txt', 'a+') as f:
                            f.write(item)
                    filterBox.clear()
    
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


    def create_widgets(self):
        self.addDomains = tk.Button(self, text="Add Addon Domains", command=self.addDomainsGui)
        self.addDomains.pack(side="top")
        
        self.addRecords = tk.Button(self, text="Add DNS Records", command=self.addDNSGui)
        self.addRecords.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",command=self.master.destroy)
        self.quit.pack(side="bottom")

if __name__ == "__main__":
    root = tk.Tk()
    app = Gui(master=root)
    app.mainloop()
