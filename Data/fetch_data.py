import os
from langchain_community.utilities import BingSearchAPIWrapper
import requests
import chardet
from bs4 import BeautifulSoup

os.environ["BING_SUBSCRIPTION_KEY"] = "BING_SUBSCRIPTION_KEY"
os.environ["BING_SEARCH_URL"] = "https://api.bing.microsoft.com/v7.0/search"

def search_keyword(keyword, num):
    search = BingSearchAPIWrapper()
    search_results = search.results(keyword, num)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # 确保 WebData 文件夹存在
    directory = './Data/WebData'
    if not os.path.exists(directory):
        os.makedirs(directory)

    # 遍历搜索结果
    for i, result in enumerate(search_results):
        # 获取网页内容
        response = requests.get(result['link'], headers=headers)
        encoding = chardet.detect(response.content)['encoding']
        content = response.content.decode(encoding)
        response.raise_for_status()

        # 创建文件名
        filename = os.path.join('./Data/WebData', f'page{i}.html')

        # 将内容写入到文件
        with open(filename, 'w', encoding=encoding) as f:
            f.write(content)

def read_web_data(web_data):
    docs = []
    for file in os.listdir(web_data):
        file_path = os.path.join(web_data, file)
        
        # 检测文件编码
        rawdata = open(file_path, 'rb').read()
        result = chardet.detect(rawdata)
        charenc = result['encoding']
        
        with open(file_path, "r", encoding=charenc) as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            text = soup.get_text()
            docs.append(text)
        os.remove(file_path)
    return docs