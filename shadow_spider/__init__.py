import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import os
from shadow_spider.setting import proxies, executable_path, service_args



#url -- http://65px7xq64qrib2fx.onion
def download_html(driver, url):
    driver.get(url)
    b = BeautifulSoup(driver.page_source, "html.parser")
    imgs = b.findAll("img")
    for i in imgs:
        i["src"] = change_url(url, i["src"])
    css = b.findAll("link", {"rel": "stylesheet"})
    for i in css:
        i["href"] = change_url(url, i["href"])
    main_folder_name = b.find("title").get_text()
    if not os.path.exists(main_folder_name):
        os.makedirs(main_folder_name)
    file_name = main_folder_name + ".html"
    f = open(main_folder_name + "/" + file_name, "wb")
    f.write(b.encode("utf-8"))
    f.close()
    return b, main_folder_name

def change_url(base_url, url):
    if url[:2] == "//" and url.find(base_url[7:]) != -1:
        url = url.replace("//" + base_url[7:] + "/", "./")
    elif url[:7] == "http://":
        url = url.replace(base_url + "/", "./")
    elif url[0] == "/" and url[1] != "/":
        url = "." + url
    elif url[0] != "/" and url[:7] != "http://" and url[:2] != "./":
        url = "./" + url
    return url

def make_folder(main_folder_name, source_url):
    if source_url[2:source_url.rfind("/")] != "":
        folders_name = main_folder_name + "/" + source_url[2:source_url.rfind("/")]
    else:
    	   folders_name = main_folder_name
    if len(folders_name) != 0:
        if not os.path.exists(folders_name):
            os.makedirs(folders_name)
    return folders_name

def download_source(s, folder, base_url, source_url):
    print("folder: ", folder, "source_url", source_url)
    if source_url.find("?") == -1:
        judge = len(source_url)
    else:
        judge = source_url.find("?")
    file_name = folder + "/" + source_url[source_url.rfind("/") + 1:judge]
    if file_name[0] == ".":
        file_name = file_name[2:]
    print("downloading filename: ", file_name)
    r = s.get(base_url + source_url[1:], proxies = proxies)
    #print(r.content)
    f = open(file_name, "wb")
    f.write(r.content)
    f.close()
    return file_name


def collect_source_url(bobj):
    url_list = []
    imgs = bobj.findAll("img")
    for i in imgs:
        url = i["src"]
        url_list.append(url)
    css = bobj.findAll("link", {"rel": "stylesheet"})
    for i in css:
        url = i["href"]
        url_list.append(url)    
    return url_list

def download(base_url):
    if base_url[-1] == "/":
        base_url = base_url[:-1]
    print(base_url)
    s = requests.Session()
    driver = webdriver.PhantomJS(executable_path = executable_path, service_args = service_args)
    b, main_folder = download_html(driver, base_url)
    print("this is:", main_folder)
    url_list = collect_source_url(b)
    for i in url_list:
        print(i)
        download_source(s, make_folder(main_folder, i), base_url, i)
    print("下载完成！")

