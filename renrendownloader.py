import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import pickle
import json
import os
import urllib
from io import BytesIO

email = '#######'
password = '#######'
userId = "#######"

blogRootUrl = 'http://blog.renren.com/blog/'

blogApi = blogRootUrl + userId + '/blogs'
statusApi = "http://status.renren.com/GetSomeomeDoingList.do?userId=" + userId
shareUrl = "http://share.renren.com/share/v7/" + userId + "?type=0"
albumListUrl = "http://photo.renren.com/photo/"+ userId +"/albumlist/v7?offset=0&showAll=1"
blogEntryUrl = "http://blog.renren.com/blog/"+ userId + "/"

photosUrl = "http://photo.renren.com/photo/264636169/album-314588998/bypage/ajax/v7?page=3&pageSize=20"

backupPath = "c:\\人人\\"

blogBackupPath = backupPath + "日志\\"

albumBackupPath = backupPath + "相册\\"

def getCookieFromNet():
    url = 'http://www.renren.com/PLogin.do'
    payload = {
        'redir': 'http://zhibo.renren.com/top',
        'email': email,
        'password': password
    }

    s.post(url, headers=headers, data=payload, verify=True)

    with open('cookies.renren', 'wb') as f:
        cookiedict = requests.utils.dict_from_cookiejar(s.cookies)
        pickle.dump(cookiedict, f)

    print('submit form, fetch cookies successfully')

    return s.cookies

def loginAndGetData():
    print('getting cookis...')

    cookies = getCookieFromNet();

    s.cookies = cookies

    getBlogs()

    getStatus()

    getShare()

    #getPhotos(str(314588998), 92)

def getPhotos(albumId, totol):
    pages = round(totol/20)

    localAlbum = albumBackupPath + str(albumId)

    if not os.path.exists(localAlbum):
        os.makedirs(localAlbum)

    for i in range(pages):
        photosUrl = "http://photo.renren.com/photo/"+ userId +"/album-"+ albumId +"/bypage/ajax/v7?page=" + str(i) + "&pageSize=20"
        photosJson = s.get(photosUrl, headers=headers).text
        data2 = json.loads(photosJson)

        photoList = data2["photoList"]

        for photo in photoList:
            photoUrl = photo["url"]

            print(photoUrl)

            req = urllib.request.Request(url=photoUrl, headers=headers)

            photo = urllib.request.urlopen(req).read()

            photoName = localAlbum + "\\" + photoUrl.split('/')[-1]

            with open(photoName, "wb",) as file:
                file.write(photo)

def getShare():
    shareFile = open(backupPath + "分享.html", "w",encoding='utf-8')

    html = s.get(shareUrl, headers=headers)
    firstShare = html.text

    soup = BeautifulSoup(firstShare, 'lxml')
    count = soup.select(".current .share-type-count")[0]
    shareContents = soup.select(".ugc-list-item")

    for content in shareContents:
        print(content)

        content.select(".share-item-footer")[0].decompose()

        shareFile.write(str(content))

    count = count.text

    pagenum = round(int(count) / 20)

    if pagenum > 0:
        for i in range(pagenum + 1):
            if i > 0:
                html = s.get(shareUrl + '&curpage=' + str(i), headers=headers)
                firstShare = html.text

                soup = BeautifulSoup(firstShare, 'lxml')
                count = soup.select(".current .share-type-count")[0]
                shareContents = soup.select(".ugc-list-item")

                for content in shareContents:
                    print(content)
                    content.select(".share-item-footer")[0].decompose()

                    shareFile.write(str(content))

    shareFile.close()

    print(count)

def getStatus():
    html = s.get(statusApi, headers=headers)

    firstStatusJson = html.text

    data2 = json.loads(firstStatusJson)

    count = data2['count']

    statusFile = open(backupPath + "状态.html", "w",encoding='utf-8')
    doingArray = data2['doingArray']

    for doing in doingArray:
        print(doing['content'])
        print(doing['dtime'])

        statusFile.write('<p>')
        statusFile.write(doing['content'])
        statusFile.write('</p>')
        statusFile.write('<p>')
        statusFile.write(doing['dtime'])
        statusFile.write('</p>')


    pagenum = round(count / 10)

    if pagenum > 0:
        for i in range(pagenum + 1):
            if i > 0:
                html = s.get(statusApi + '&curpage=' + str(i), headers=headers)

                firstStatusJson = html.text

                data2 = json.loads(firstStatusJson)

                doingArray = data2['doingArray']

                for doing in doingArray:
                    print(doing['content'])
                    print(doing['dtime'])

                    statusFile.write('<p>')
                    statusFile.write(doing['content'])
                    statusFile.write('</p>')
                    statusFile.write('<p>')
                    statusFile.write(doing['dtime'])
                    statusFile.write('</p>')

    statusFile.close()

def getBlogs():
    html = s.get(blogApi, headers=headers)

    firstBlogsJson = html.text

    data2 = json.loads(firstBlogsJson)

    count = data2['count']

    blogdata = data2['data']

    parseBlogEntry(blogdata)

    pagenum = round(count / 10)

    if pagenum > 0:
        for i in range(pagenum + 1):
            if i > 0:
                html = s.get(blogApi + '?curpage=' + str(i), headers=headers)

                firstBlogsJson = html.text

                data2 = json.loads(firstBlogsJson)

                blogdata = data2['data']

                parseBlogEntry(blogdata)

def parseBlogEntry(blogdata):
    for d in blogdata:
        print(d['title'])

        title = d['title']

        id = str(d['id'])

        id = id[0:9]

        blogurl = blogEntryUrl + id

        bloghtml = s.get(blogurl, headers=headers)

        soup = BeautifulSoup(bloghtml.text, 'lxml')

        blogDetail = soup.select('.blogDetail-text')[0]
        blogDate = soup.select('.blogDetail-ownerOther-date')[0]

        blogDetail = str(blogDetail)
        blogDate = str(blogDate)

        if not os.path.exists(blogBackupPath):
            os.makedirs(blogBackupPath)

        with open(blogBackupPath + title + ".html", "w",encoding='utf-8') as file:
            file.write(blogDetail)
            file.write(blogDate)

if __name__  == '__main__':
    s = requests.session()
    ua = UserAgent()
    headers = {'User-Agent': ua.chrome}

    if not os.path.exists(backupPath):
        os.makedirs(backupPath)


    loginAndGetData()