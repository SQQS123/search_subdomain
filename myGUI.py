import os
import sys
import tkinter as tk
import threading
# import queue      # 多线程一般会和queue配合使用，但是技术水平目前还达不到
import requests

from utils_sq import str_gen,prefix_str_gen

headers = {
	        "Host": "",
	        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0',
	        "Accept": " text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
	        "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
	        "Accept-Encoding": "gzip, deflate",
	        "Connection": "close",
	        }

# 26的5次方，表示搜索完5位以下的所有可能,只要计算性能牛逼完全可以设置得更大
GLOB_MAX_CNT = 11881377

class InsertContent():
    def __init__(self,queue):
        self.queue = queue

    def write(self,content):
        self.queue.put(content)
    

# 设计为面向对象的方式
# 参考网址：https://blog.csdn.net/u013700771/article/details/103321783
class GUI():
    def __init__(self,root):
        self.LOCK = False
        # self.msg_queue = queue.Queue()
        self.initGUI(root)

    def initGUI(self,root):
        self.root = root
        self.root.geometry("500x300+700+500")
        self.root.resizable = False
        self.domainLabel = tk.Label(text='请输入域名：')
        self.domainLabel.pack(side=tk.TOP)
        self.domainEntry = tk.Entry(show=None,width=30)
        self.domainEntry.pack()
        self.searchBtn = tk.Button(text='开始查询',command=lambda:self.search_subdomain(self.domainEntry.get()))
        self.searchBtn.pack(side=tk.TOP)

        # self.text = tk.Text(root, height=10, width=45, yscrollcommand=self.scrollBar.set)
        self.text = tk.Text(root, height=10, width=45)
        self.text.pack()

        self.scrollBar = tk.Scrollbar(self.text)

        # self.root.after(10, self.show_msg)
        # sys.stdout = InsertContent(self.msg_queue)

        # 优雅地杀死所有线程
        self._stop_event = threading.Event()

        self.root.mainloop()
        self.stop()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def __search_subdomain(self,*domain):
        # 以下实现查询子域名的功能
        # 首先判断是否存在子域名字典
        if self.stopped():
            return
        if os.path.exists('./dic.txt'):
            sub_str_gen = open('./dic.txt','r')
        else:
            s = ""
            for c in domain:
                s+=c
            headers["Host"] = "www." + s
            # sub_str_gen = str_gen()
            # 可以最先通过暴力破解的方式生成子域名，如果访问成功则将该生成的字符串添加到字典
            g = prefix_str_gen(GLOB_MAX_CNT)
            for prefix_str in g:
                url = "http://"+prefix_str+ '.'+s
                try:
                    res = requests.get(url,headers)
                except Exception as e:
                    res = None
                if res == None:
                    continue
                if res.status_code != 200:
                    continue
                print(prefix_str+ '.'+s)
                # 在这里实现后续工作
                # 。。。
                if not self.LOCK:
                    # 插入
                    self.LOCK = True
                    with open("./result.txt","a") as f:
                        f.writelines(url +'\n')
                    self.text.insert(tk.INSERT,url +'\n')
                    self.text.see(tk.END)
                    self.LOCK = False
                if self.stopped():
                    break

    def search_subdomain(self,domain):
        if self.searchBtn['text'] == '停止':
            self.stop()
            self.searchBtn['text'] = '开始'
            return
        if not domain or len(domain.split('.'))<2:
            self.domainEntry.delete(0,tk.END)
            self.domainEntry.insert(tk.END,'请输入正确域名') 
            return
        self.T = threading.Thread(target=self.__search_subdomain,args=(domain))
        self.searchBtn['text'] = '停止'
        self.T.start()