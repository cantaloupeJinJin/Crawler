"""
爬取上海市所有道路的形状坐标，并以json文件格式存储
"""
from urllib.parse import quote
from urllib import request
import json
import xlrd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

amap_web_key = '你的key'
poi_search_url = "http://restapi.amap.com/v3/place/text"
poi_boundary_url = "https://www.amap.com/service/poiInfo?query_type=IDQ&qii=true&need_utd=true&utd_sceneid=1000&addr_poi_merge=true&is_classify=true"
cityname = "上海"
classfiled = "道路名"
read_file_dir = "道路名.xls"
save_file_dir = "road.json"
#no_sheet:sheet的编号,no_cell_value:列编号
no_sheet = 0
no_cell_value = 0

# 根据id获取边界数据
def getBounById(id):
    req_url = poi_boundary_url + "&key=" + amap_web_key + "&id=" + id
    with request.urlopen(req_url) as f:
        data = f.read()
        data = data.decode('utf-8')
        dataList = []
        datajson = json.loads(data)  # 将字符串转换为json
        #print(datajson)
        if len(datajson) < 1:
            return dataList
        datajson = datajson['data']
        datajson = datajson['poi_list'][0]
        datajson = datajson['domain_list'][3]
        if datajson.get('value') != None:
            datajson = datajson['value']
            dataArr = [x.split('|') for x in datajson.split('_')]
            for i in dataArr:
                innerList = []
                #每个innerList存储一对数据
                f = i[0].split(',')

                innerList.append(float(f[0]))
                innerList.append(float(f[1]))
                #print(innerList)
                dataList.append(innerList)
        return dataList

def readname():
    myWordbookr = xlrd.open_workbook(read_file_dir)
    mySheetsr = myWordbookr.sheets()
    mySheetr = mySheetsr[no_sheet]
    # 获取列数
    nrows = mySheetr.nrows
    with open(save_file_dir, "w") as fp:
        for i in range(1, nrows):
            # delay = 800000
            # while delay > 0:
            #     delay -= 1
            id = mySheetr.cell_value(i, no_cell_value)
            roadname = mySheetr.cell_value(i, 1)
            address = mySheetr.cell_value(i, 2)
            boundarydata = getBounById(id)
            tmp = {
                "features": [
                    { "attributes": {
                            "FID": i,
                            "名称": roadname,
                            "区": address
                        },
                        "geometry": {
                            "paths": [
                               boundarydata
                            ]
                        }
                    }
                ]
            }
            print(tmp)
            fp.write(json.dumps(tmp, indent=4, ensure_ascii=False))
            if i % 100 == 0:
                print("sleep")
                delay = 800000000
                while delay > 0:
                    delay -= 1
                print("stopsleep")


    print('写入成功')

readname()


# 根据获取到的poi数据的id获取边界数据
#dataList = getBounById('B0FFGQ7PQK')
#print(dataList)
#print(str(dataList))
