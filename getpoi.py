"""
获取上海所有POI的id,name,location（经纬度坐标）,adname（所属区，如徐汇区），并将爬取的数据存入json文件中
注意：该爬取方法未对数据进行去重
"""
from urllib.parse import quote
from urllib import request
import json
import xlwt
import xlrd
import test

#https://restapi.amap.com/v3/place/polygon?key=e28ed3ab9b8b955626b7a0247d6cea68&polygon=
# 120.856804,30.675593|121.856804,31.675593&keywords="道路名"&types=190301&offset=20&page=1
# &extensions=all

#efdaa20612fea6092643acd3c1fd7756
#e28ed3ab9b8b955626b7a0247d6cea68
amap_web_key = 'efdaa20612fea6092643acd3c1fd7756'
search_url = 'https://restapi.amap.com/v3/place/polygon'
save_file = "POI.json"

#typename = "道路名"
#types = '190301'
#typename以及types在高德提供的相关文档中下载，https://lbs.amap.com/api/webservice/download

#根据高德给定的 https://lbs.amap.com/api/webservice/guide/api/district  获得上海市四边形边界
maxlatitude = 122.247149
minlatitude = 120.856804
maxlongitude = 31.872716
minlongitude = 30.675593

#polylist 存储所有网格的四边形边界
def write_to_excel(polylist, typenametypes):
    with open(save_file, 'w') as f:
        j = 0
        nomber = 1
        for polygon in polylist:
            print("第%d个方格区域搜索" %nomber)
            for typenametype in typenametypes:
                all_pages = get_roads(polygon, typenametype[0], typenametype[1])
                len_pages = len(all_pages)
                #print("allpages:", all_pages)
                #print(len_pages, typenametype[0], typenametype[1])
                k = 0
                for i in range(j, j + len_pages):
                    name = all_pages[k][1]
                    address = all_pages[k][2]
                    strlocation = all_pages[k][3]
                    tmp = strlocation.split(',')
                    location = []
                    location.append(float(tmp[0]))
                    location.append(float(tmp[1]))
                    tmp = {
                        "features": [
                            {"attributes": {
                                "FID": i,
                                "名称": name,
                                "区": address
                            },
                                "geometry": {
                                    "paths": [
                                        location
                                    ]
                                }
                            }
                        ]
                    }
                    print(tmp)
                    f.write(json.dumps(tmp, indent=4, ensure_ascii=False))
                    k += 1
                j += len_pages
            nomber += 1
        f.close()


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
def get_roads(polygon, typename, types):
    i = 1
    all_pages = []
    while True:
        results = get_page_road(polygon, typename, types, i)
        if results == []:
            break
        all_pages += results
        i += 1
    return all_pages

#获取每一页的数据
def get_page_road(polygon, typename, types, page):
    try:
        req_url = search_url + "?polygon=" + polygon + "&keywords=" + quote(typename) + "&types=" + \
                  types + "&offset=" + str(20) + "&page=" + str(
            page) + "&extensions=all" + "&output=json" + "&key=" + amap_web_key
    except:
        return []
    with request.urlopen(req_url) as f:
        data = f.read()
        data = data.decode('utf-8')
        idlist = []
        datajson = json.loads(data)  # 将字符串转换为json
        if datajson.get('pois') != None:
            datajson = datajson['pois']
            #print(datajson)
            for i in range(len(datajson)):
                if datajson[i]['cityname'] == "上海市":
                    tmp = []
                    tmp.append(datajson[i]['id'])
                    tmp.append(datajson[i]['name'])
                    tmp.append(datajson[i]['adname'])
                    tmp.append(datajson[i]['location'])
                    idlist.append(tmp)
            #print(idlist)
        return idlist

#读取所有的type以及typename
def get_type():
    myWordbook = xlrd.open_workbook('amap_poicode.xlsx')
    mySheets = myWordbook.sheets()
    mySheet = mySheets[2]
    # 获取列数
    nrows = mySheet.nrows
    typelist = []
    for i in range(1, nrows):
        tmp = []
        tmp.append(mySheet.cell_value(i, 4))
        tmp.append(mySheet.cell_value(i, 1))
        typelist.append(tmp)
    return typelist

# poly = "120.856804,30.675593|121.856804,31.675593"
# get_page_road(poly, 1)
#polylist = get_polys(maxlatitude, maxlongitude, minlatitude, minlongitude)
typelists = get_type()
polylists = generalID(4, 4)
write_to_excel(polylists, typelists)
