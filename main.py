import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import schedule
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import dont_share as ds
numList = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


class Yahoo:
    def __init__(self):
        self.mark = []
        self.alter = []
        self.valid = []

    @staticmethod
    def get_online_data():
        data = pd.DataFrame = pd.read_csv('guitars.csv', names=['guitar', 'num'], header=0)
        return data

    def search_goods(self, url, name):
        proxies = {'http': 'http://127.0.0.1:7890', 'https': 'http://127.0.0.1:7890'}
        flag = [0] * len(name)
        jump = 0
        index = 0
        for i in name:
            if i in numList:
                flag[index] = -1
            else:
                flag[index] = 1
            index = index+1

        for j in range(len(name)-1):
            if flag[j] != flag[j+1]:
                jump = jump+1

        if flag[0] == -1:
            num_numbers = int(jump/2) + 1
        else:
            num_numbers = int((jump+1)/2)

        response = requests.get(url=url, proxies=proxies)
        html = response.text

        soup = BeautifulSoup(html, 'html.parser')
        soup.prettify()

        description = soup.find(attrs={"name": "description"})['content']
        info = str(description)
        info = info.replace(',', '')
        print(info)
        num = int(re.findall("\\d+", info)[num_numbers])
        if num > 100:
            self.valid.append(0)
        else:
            self.valid.append(1)
        return num

    def update(self):
        data = Yahoo.get_online_data()
        for index in range(data.shape[0]):
            yahoo = 'https://auctions.yahoo.co.jp/search/search?auccat=&tab_ex=commerce&ei=utf-8&aq=-1&oq=&sc_i=&fr=auc_top&p=' + data.guitar[index]+'&x=0&y=0'
            name = data.guitar[index]
            num_searched = Yahoo.search_goods(self, yahoo, name)
#            print(data.guitar[index])
            print(num_searched)
            if data.num[index] < num_searched:
                self.alter.append(int(num_searched-data.num[index]))
                self.mark.append(1)
                #print(self.alter[index])

                #print(str(data.guitar[index])+' has '+str(self.alter[index])+' new goods in yahoo auctions')
                data.loc[index, 'num'] = num_searched

            elif data.num[index] > num_searched:
                self.alter.append(int(data.num[index]-num_searched))
                self.mark.append(-1)

                #print(self.alter[index])
                #print(str(data.guitar[index])+' has '+str(self.alter[index])+' auctions end')
                data.loc[index, 'num'] = num_searched

            else:
                #print(str(data.guitar[index])+' has nothing changed')
                self.mark.append(0)
                self.alter.append(int(0))

        data.to_csv('guitars.csv')

    def create_email(self):
        data = Yahoo.get_online_data()
        flag = 0
        for index in range(data.shape[0]):
            if self.mark[index] != 0 and self.valid[index] != 0:
                flag = 1
        if flag == 1:
            text = 'found some new guitars for you : )\n'
            for index in range(data.shape[0]):
                if self.mark[index] == 1 and self.valid[index] != 0:
                    text += (str(self.alter[index])+' '+str(data.guitar[index])+' new autions\n')
                elif self.mark[index] == -1 and self.valid[index] != 0:
                    text += (str(self.alter[index])+' '+str(data.guitar[index])+' auctions end\n')
        else:
            text = 'Nothing happened.'

        return text, flag

    def send_email(self):
        text, flag = Yahoo.create_email(self)
        if flag == 1:
            msg = MIMEText(text, 'plain', 'utf-8')
            from_address = ds.from_address
            password = ds.password
            to_address = ds.to_address
            server = smtplib.SMTP_SSL('smtp.gmail.com')
            server.connect('smtp.gmail.com', 465)
            server.login(from_address, password)
            server.sendmail(from_address, to_address, msg.as_string())
            server.quit()
            print('Gmail sended')
        else:
            print('Nothing changed, do not send email')


# schedule.every().minute.do(Guitar.update)
yahoo = Yahoo()
yahoo.update()
yahoo.send_email()
