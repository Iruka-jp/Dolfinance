#from selenium import webdriver
from msedge.selenium_tools import Edge, EdgeOptions
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests

mkt_sections={"First Section":0 , "Second Section":1 , "Mothers":2 , "JASDAQ":3 , "TOKYO PRO Market":4 , "First Section Foreign Stocks":5 , "Second Section Foreign Stocks":6 , "Mothers Foreign Stocks":7 , "ETF":8 , "ETN":9 , "Real Estate Investment Trust (REIT)":10 , "Preferred equity contribution certificate":11 , "Others":12}

class FinDataScrapper:
    def __init__(self, driver_path, market = "tse", section_name = "First Section"):
        options = EdgeOptions()
        options.use_chromium = True
        options.add_argument("headless")
        self.driver = Edge(executable_path=driver_path,options=options)
        self.market = market
        self.section_name = section_name
        self.listed_stocks = pd.DataFrame(columns=['Stock Symbol', 'Company name', 'Industry', 'Market section', 'Trading unit'])

        self.debug = 0

    def getListedStock(self):
        self.listed_stocks.drop(self.listed_stocks.index[:], inplace =True)
        if(self.market == "tse"):
            self.driver.get("https://www2.tse.or.jp/tseHpFront/JJK020010Action.do") # go to the url
            Script = """document.getElementsByName('dspSsuPd').item(0).options[3].selected = true;
            document.getElementsByName('szkbuChkbx').item({}).checked= true;""".format(mkt_sections[self.section_name])
            self.driver.execute_script(Script)
            searchButton = self.driver.find_element_by_name("searchButton")
            searchButton.click()
            self.parseTable()

        else:
            print("This market is not yet covered")

    def parseTable(self):
        if(self.market == "tse"):
            print(self.debug)
            self.debug +=1
            stockSymbol=[]
            section=[]
            tradUnit=[]
            compName=[]
            industry=[]
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            tableCells = soup.find_all("td")
            for i,x in enumerate(tableCells[:-2]): #the last two td are from a different table
                if(i%11==0):
                    stockSymbol.append(x.find('input').get('value'))
                elif(i%11==1):
                    section.append(x.find('input').get('value'))
                elif(i%11==4):
                    tradUnit.append(x.find('input').get('value'))
                elif(i%11==8):
                    compName.append(x.find('input').get('value'))
                elif(i%11==9):
                    industry.append(x.find('input').get('value'))

            df = pd.DataFrame({'Stock Symbol': stockSymbol, 'Company name': compName,
                               'Industry':industry, 'Market section':section, 'Trading unit':tradUnit})
            self.listed_stocks = self.listed_stocks.append(df,ignore_index=True)

            nextButtons = self.driver.find_elements_by_class_name("next_e")

            try:
                link = nextButtons[0].find_element_by_tag_name("a")
            except:
                print("Parsed all the pages")
            else:
                link.click()
                self.parseTable()

        else:
            print("This market is not yet covered")

    def save_stock_list(self):
        self.listed_stocks.to_csv("{}_{}.csv".format(self.market, self.section_name), index=False)

    def get_stock_fillings(self, ticker):
        self.driver.get("https://www2.tse.or.jp/tseHpFront/JJK020010Action.do") # go to the url
        tic = self.driver.find_element_by_name('eqMgrCd')
        tic.send_keys(int(ticker))
        searchButton = self.driver.find_element_by_name("searchButton")
        searchButton.click()
        Script = """document.forms['JJK020030Form'].mgrCd.value = {};
        document.forms['JJK020030Form'].jjHisiFlg.value = '1';
        submitPage(document.forms['JJK020030Form'], document.forms['JJK020030Form'].BaseJh);""".format(ticker)
        self.driver.execute_script(Script)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        links = [(''.join(link.text.split()), 'https://www2.tse.or.jp' + link.get('href')) for link in links if 'ＩＦＲＳ' in link.text]
        compamyName = self.driver.find_element_by_class_name('fontsizeM').text

        dir = 'fillings/{}'.format(compamyName + '_' + ticker)
        if not os.path.exists('fillings'):
            os.makedirs('fillings')
        if not os.path.exists(dir):
            os.makedirs(dir)

        for link in links:
            if not os.path.exists(dir + '/' + link[0] + '.pdf'):
                r = requests.get(link[1], stream=True)
                with open(dir + '/' + link[0] + '.pdf', 'xb') as f:
                    f.write(r.content)




if __name__ == '__main__':
    driver_path = r'C:/dev/WebDrivers/edgedriver_win64_93/msedgedriver.exe'
    fds = FinDataScrapper(driver_path)
    fds.get_stock_fillings('69020')
