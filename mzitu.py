from bs4 import BeautifulSoup
import os
from third.Download import down
from pymongo import MongoClient
import datetime

class mzitu():

    def __init__(self):
        client = MongoClient() # 与MongoDB建立链接(这是默认连接本地MongoDB数据库)
        db = client['BeautyCollection'] # 选择一个数据库
        self.meizitu_collection = db['meizitu'] # 在BeautyCollection数据库中，选择一个集合
        self.title = '' # 用来保存页面主题
        self.url = '' #用来保存页面地址
        self.img_urls = [] # 初始化一个列表，用来保存图片地址

    # 爬取所有的图片连接
    def all_url(self, url):
        html = down.get(url, 3)
        all_a = BeautifulSoup(html.text, 'lxml').find('div', class_='all').find_all('a')
        for a in all_a:
            title = a.get_text()
            self.title = title # 将主题保存到self.title中
            print(u'开始保存', title)
            path = str(title).replace('?', "_").replace('/', '')
            self.mkdir(path)
            path = self.parse_path(path)
            # 切换到该目录
            os.chdir(path)
            href = a['href']
            self.url = href # 将页面地址保存到self.url中
            # 判断这个主题是否已经在数据库中、不在就运行else下的内容，在则忽略。
            if self.meizitu_collection.find_one({'PAGE': href}):
                print(u'这个页面已经爬取过了')
            else:
                self.html(href)


    # 爬取图片页面中图片的最大数和获取每一个图片的链接
    def html(self, href):
        html = down.get(href, 3)
        max_span = BeautifulSoup(html.text, 'lxml').find('div', class_='pagenavi').find_all('span')[-2].get_text()
        print(u'此图集共', max_span, '张图集')
        page_num = 0 # 当作计数器
        for page in range(1, int(max_span)+1):
            page_num = page_num + 1 # 每for循环一次就+1(当page_num==max_span时，就是到了最后一张了)
            page_url = href + '/' + str(page)
            self.img(page_url, max_span, page_num)

    # 到每一张图片之下，开始访问图片链接
    def img(self, page_url, max_span, page_num):
        img_html = down.get(page_url, 3)
        img_url = BeautifulSoup(img_html.text, 'lxml').find('div', class_='main-image').find('img')['src']
        self.img_urls.append(img_url)
        # 传递下来的参数可以使用上了，当max_span和page_num相等时，就是最后一张图片了
        if int(max_span) == page_num:
            self.save(img_url)
            post = {
                'TITLE': self.title,
                'PAGE': self.url,
                'IMG_URI': self.img_urls,
                'GET_TIME':datetime.datetime.now()
            }
            self.meizitu_collection.save(post) # 将post内容写入数据库中
            print(u'插入数据库成功,共',page_num,'张图片')
            self.img_urls = []  # 每次爬完一个图集清空一次img_urls,否则后面img_urls会很臃肿
        # 如果max_span 不等于 page_num则执行下面这句话
        else:
            self.save(img_url)

    def save(self, img_url):
        # name = img_url[-9:-4]
        name = img_url.split('/')[-1]
        print(u'开始保存：', img_url)
        img = down.get(img_url, 3)
        # f = open(name + '.jpg', 'ab')
        f = open(name, 'ab')
        f.write(img.content)
        f.close()

    def mkdir(self, path):
        path = path.strip()
        isExists = os.path.exists(os.path.join('/home/jerusalemsbell/Downloads/Mzitu/', path))
        if not isExists:
            print(u'建立了一个名字叫做', path, u'的文件夹')
            os.mkdir(os.path.join('/home/jerusalemsbell/Downloads/Mzitu/', path))
            return True
        else:
            print(u'名字叫做', path, u'的文件夹已经存在了')
            return False


    def parse_path(self, path):
        path = path.strip()
        path = path
        path = '/home/jerusalemsbell/Downloads/Mzitu/'+path
        return path

Mzitu = mzitu()
Mzitu.all_url('http://www.mzitu.com/all')