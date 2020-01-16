"""
获取上海所有道路的id,name
"""
from urllib.request import quote
from urllib import request
import json
import xlwt
import test

#https://restapi.amap.com/v3/place/polygon?key=你的keyy&polygon=
# 120.856804,30.675593|121.856804,31.675593&keywords="道路名"&types=190301&offset=20&page=1
# &extensions=all
amap_web_key = '你的key'
search_url = 'https://restapi.amap.com/v3/place/polygon'
roadname = "道路名"
types = '190301'

#根据高德给定的 https://lbs.amap.com/api/webservice/guide/api/district  获得上海市四边形边界
maxlatitude = 122.247149
minlatitude = 120.856804
maxlongitude = 31.872716
minlongitude = 30.675593

#polylist 存储所有网格的四边形边界
def write_to_excel(polylist):
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet(roadname, cell_overwrite_ok=True)

    # 第一行(列标题)
    sheet.write(0, 0, 'id')
    sheet.write(0, 1, 'name')
    sheet.write(0, 2, 'address')
    j = 0
    for polygon in polylist:
        all_pages = get_roads(polygon)
        len_pages = len(all_pages)
        print(len_pages)
        k = 0
        for i in range(j,j+len_pages):
            # 每一行写入
            sheet.write(i + 1, 0, all_pages[k][0])
            sheet.write(i + 1, 1, all_pages[k][1])
            sheet.write(i + 1, 2, all_pages[k][2])
            k += 1
        j += len_pages
    book.save(r'' + roadname + '.xls')

"""
根据范围划分网格，获得每个网格的四边形边界
"""
def generalID(column_num,row_num):
    latitude = (maxlatitude - minlatitude)/column_num
    longitude = (maxlongitude - minlongitude)/row_num
    print("maxlatitude", maxlatitude,"minlatitude",minlatitude,"latitude",latitude,"column_num",column_num)
    polylists = []

    for i in range(column_num):
        left_latitude = minlatitude + latitude * i
        righ_latitude = minlatitude + latitude * (i+1)
        for j in range(row_num):
            temp = ""
            left_longitude = minlongitude + longitude * j
            righ_longitude = minlongitude + longitude * (j+1)
            temp = str(left_latitude) + ',' + str(left_longitude) + '|' + str(righ_latitude) + ',' + str(righ_longitude)
            polylists.append(temp)
    return polylists

# def get_polys(maxlatitude, maxlongitude, minlatitude, minlongitude):
#     polylist = ["120.856804,30.675593|121.856804,31.675593", "120.856804,30.675593|121.856804,31.675593"]
#     return  polylist

#获取所有页的数据
def get_roads(polygon):
    i = 1
    all_pages = []
    while True:
        results = get_page_road(polygon, i)
        if results == []:
            break
        all_pages += results
        i += 1
    return all_pages

#获取每一页的数据
def get_page_road(polygon, page):
    req_url = search_url + "?polygon="+ polygon + "&keywords=" + quote(roadname) + "&types=" + \
              types + "&offset=" + str(20) + "&page=" + str(page) + "&extensions=all"+ "&output=json" + "&key=" + amap_web_key
    with request.urlopen(req_url) as f:
        data = f.read()
        data = data.decode('utf-8')
        idlist = []
        datajson = json.loads(data)  # 将字符串转换为json
        datajson = datajson['pois']
        #print(datajson)
        for i in range(len(datajson)):
            if datajson[i]['cityname'] == "上海市":
                tmp = []
                tmp.append(datajson[i]['id'])
                tmp.append(datajson[i]['name'])
                tmp.append(datajson[i]['address'])
                idlist.append(tmp)
        #print(idlist)
        return idlist

# poly = "120.856804,30.675593|121.856804,31.675593"
# get_page_road(poly, 1)
#polylist = get_polys(maxlatitude, maxlongitude, minlatitude, minlongitude)
polylists = generalID(11, 11)
print(polylists)
write_to_excel(polylists)
