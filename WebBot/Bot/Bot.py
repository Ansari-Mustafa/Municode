import time
import simple_colors
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import textract

def clear_results(file_name):
    with open(file_name,'w') as file:
        pass
    file.close()

class AutoBot(webdriver.Edge):
    def __init__(self, driver_path=r"C:\SeleniumDriver\msedgedriver.exe", teardown=False):
        self.driver_path = driver_path
        self.teardown = teardown
        self.post_no = 1
        self.all_posts = [{0}]
        self.download = None
        self.state_urls = []

        super(AutoBot, self).__init__()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.teardown:
            print("Quitting...")
            self.quit()

    def open_url(self, url):
        self.get(url)
        self.maximize_window()

    def select_state(self, state=None):
        self.implicitly_wait(5)
        self.find_element(by='xpath', value=f'//ul[@class="nav row"]/li/a[text()= "{state}"]').click()
        self.implicitly_wait(15)

    def select_county(self, county=None):
        self.implicitly_wait(5)
        self.find_element(by='xpath', value=f'//li[@ng-repeat="client in letterGroup.clients"]/a[text() = "{county}"]'
                          ).click()
        self.implicitly_wait(15)

    def search_bar(self, search=None):
        self.find_element(by='id', value='headerSearch').send_keys(Keys.BACK_SPACE*35, search, Keys.ENTER)

    def search_per_page(self, posts):
        self.find_element(by='id', value='pageResultsSize').click()
        self.find_element(By.XPATH, f"//option[@label='{posts}']").click()

    def get_all_headings(self, top=None):
        self.top3_results = []
        # self.all_posts = self.find_elements(by='xpath', value='//h4[@class="text-normal result-title"]')
        for i in range(top):
            self.top3_results.append(self.find_element(by='xpath', value=f'//div[@style="overflow: hidden;"]/div[{i}]/div/div/div/h4/a').text)

    def save_result(self):
        self.implicitly_wait(15)
        headings = self.find_elements(by='xpath', value='//div[@class="chunk-title"]')
        contents = self.find_elements(by='xpath', value='//div[@ng-switch-when="1"]')
        for heading in headings:
            if heading.text in self.top3_results:
                saved_elements = contents[headings.index(heading)]
                self.top3_results[self.top3_results.index(heading.text)] = " "    
                with open("WebData/Results.txt", 'a', encoding='utf-8') as saved_content:
                    saved_content.write(saved_elements.text)
                    saved_content.close()
    
    def get_top_results(self, top=None):
        try:
            self.top3_results = []
            for i in range(top):
                self.top3_results.append(self.find_element(by='xpath', value=f'//div[@style="overflow: hidden;"]/div[{i+1}]/div/div/div/h4/a').text)
            for i in range(top):
                if i == 0:
                    self.find_element(by='xpath', value=f'//div[@style="overflow: hidden;"]/div[1]/div/div/div/h4/a').click()
                elif i >= 1:
                    self.implicitly_wait(30)
                    result_element = self.find_element(by='xpath', value=f'//a[@class="text-primary" and text() = "{self.top3_results[i]}"]')
                    self.implicitly_wait(15)
                    result_element.click()
                time.sleep(5)
                self.save_result()
        except NoSuchElementException:
            print("All Saved!")

    def download_pdf(self):
        self.find_element(by='xpath', value='//div[@class="col-md-9"]/button').click()
        self.find_element(By.CSS_SELECTOR, 'button[data-actionid="print"]').click()

    def download_sections(self):
        # Download file
            self.find_element(by='xpath', value=f'//div[@style="overflow: hidden;"]/div[{self.post_no}]/div/div/div/div'
                              ).click()
            self.find_element(By.CSS_SELECTOR, 'button[data-actionid="download"]').click()
            print(simple_colors.cyan("Download saved!"))

    def get_web_data():
        print(str(textract.process("C:/Users/Archiwiz1/Downloads/PinellasCountyFLCodeofOrdinances.docx")))

    def save_states(self):
        state_text_file = open("USA/states.txt", 'a')
        self.open_url("https://library.municode.com/")
        self.implicitly_wait(5)
        state_list = []
        states = self.find_elements(by='xpath', value='//ul[@class="nav row"]/li/a')
        for state in states:
            state_list.append(state.text)
            self.state_urls.append(state.get_attribute('href'))
            state_text_file.write(f"{state.text}\n")
        return state_list

    def save_cities(self):
        city_list = []
        for url in self.state_urls:
            self.open_url(url) 
            city_text_file = open(f"USA/{self.state_urls.index(url)}.txt", 'a')
        
            self.implicitly_wait(15)
            cities = self.find_elements(by='xpath', value='//ul[@class="nav row"]/li/a')
            for city in cities:
                city_list.append(city.text)
                city_text_file.write(f'{city.text}\n')

'''
    def plant_pricing(self, plant=None):
        all_plants = self.find_elements(by='xpath', value=f"//div[@class='catalog-item']")
        print(len(all_plants))
        for item in all_plants:
            if plant in item.text:
                header_element = item.find_element(by='xpath', value="./article/header/h2")
                price_element = item.find_element(by='xpath', value="./article/div/div/div/a")
                print(f'Plant = {header_element.text}')
                print('Price =', price_element.text.replace("starting at", " ").strip())
'''
"""        if print_data:
            for post in self.all_posts:
                print(simple_colors.cyan(f'Result No.{self.all_posts.index(post) + 1}:', ['bold', 'underlined']))
                print(simple_colors.magenta(f'{post.text} \n'))

        # self.post_no = int(input("Enter the result no. you want to view in more detail:\n>"))
        # self.implicitly_wait(5)
"""