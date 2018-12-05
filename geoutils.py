# -*- coding: utf-8 -*-

import math
import sys
import re
import hashlib
from math import cos, sin, atan2, sqrt, pi ,radians, degrees,atan,tan,acos

__base32 = '0123456789bcdefghjkmnpqrstuvwxyz'
x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 扁率


def to_md5(s):
    return hashlib.md5(str(s).encode('utf-8')).hexdigest()

def to_geohash(longitude, latitude, precision=12):
    """
    Encode a position given in float arguments latitude, longitude to
    a geohash which will have the character count precision.
    """
    lat_interval, lon_interval = (-90.0, 90.0), (-180.0, 180.0)
    geohash = []
    bits = [ 16, 8, 4, 2, 1 ]
    bit = 0
    ch = 0
    even = True
    while len(geohash) < precision:
        if even:
            mid = (lon_interval[0] + lon_interval[1]) / 2
            if longitude > mid:
                ch |= bits[bit]
                lon_interval = (mid, lon_interval[1])
            else:
                lon_interval = (lon_interval[0], mid)
        else:
            mid = (lat_interval[0] + lat_interval[1]) / 2
            if latitude > mid:
                ch |= bits[bit]
                lat_interval = (mid, lat_interval[1])
            else:
                lat_interval = (lat_interval[0], mid)
        even = not even
        if bit < 4:
            bit += 1
        else:
            geohash += __base32[ch]
            bit = 0
            ch = 0
    return ''.join(geohash)




def haversine(lon1, lat1, lon2, lat2): # 经度1，纬度1，经度2，纬度2 （十进制度数）  
    """ 
    Calculate the great circle distance between two points  
    on the earth (specified in decimal degrees) 
    """  
    # 将十进制度数转化为弧度  
    lon1, lat1, lon2, lat2 = map(math.radians, [float(lon1), float(lat1), float(lon2), float(lat2)])  
    # haversine公式  
    dlon = lon2 - lon1   
    dlat = lat2 - lat1   
    _a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2  
    earth_radius = 6378137 # 地球平均半径，单位为米 
    return 2 * math.asin(math.sqrt(_a)) * earth_radius 

def calcDistance(Lng_A, Lat_A, Lng_B, Lat_B):# 经度1，纬度1，经度2，纬度2 （十进制度数） 
    ra = 6378.140
    rb = 6356.755
    flatten = (ra - rb) / ra
    rad_lat_A = radians(Lat_A)
    rad_lng_A = radians(Lng_A)
    rad_lat_B = radians(Lat_B)
    rad_lng_B = radians(Lng_B)
    pA = atan(rb / ra * tan(rad_lat_A))
    pB = atan(rb / ra * tan(rad_lat_B))
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (xx + dr)
    return distance * 1000

def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)



class MapDotter():
    def __init__(self, fname):
        self.fname = fname
        self.add_count = 0
        self.prefix = '''
        <!doctype html>
        <html lang="en" >
        <head>
            <meta charset="utf-8">
            <meta http-equiv="X-UA-Compatible" content="chrome=1">
            <meta name="viewport" content="initial-scale=1.0, user-scalable=no, width=device-width">
            <link rel="stylesheet" href="http://a.amap.com/jsapi_demos/static/resource/commonStyle.css"/>
            <title>dadian</title>
        </head>
        <body >
            <div id="container" class="map" tabindex="0"></div>
        
            <script type="text/javascript" src = 'http://webapi.amap.com/maps?v=1.4.1&key=您申请的key值'></script>
            <script type="text/javascript">
            var map = new AMap.Map('container', {
                zoom: 12,
                center: [116.414211,39.911046]
            });
            map.setMapStyle('amap://styles/darkblue');
            map.setFeatures(['point', 'building', 'road'])
            var style = [
                            {
                                url: 'http://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
                                anchor: new AMap.Pixel(6, 6),
                                size: new AMap.Size(18, 18)
                            },
                            {
                            url: 'icons/green_plus.png',
                            anchor: new AMap.Pixel(6, 6),
                            size: new AMap.Size(18, 18)
                            },
                            {
                            url: 'icons/red_marker.png',
                            anchor: new AMap.Pixel(14, 14),
                            size: new AMap.Size(17, 17)
                            },
                            {
                            url: 'icons/black_person.png',
                            anchor: new AMap.Pixel(13, 13),
                            size: new AMap.Size(25, 25)
                            }, 
                            {
                            url: 'icons/darkblue_arrow.png',
                            anchor: new AMap.Pixel(13, 13),
                            size: new AMap.Size(25, 25)
                            }, 
                            {
                            url: 'icons/grey_eclipse.png',
                            anchor: new AMap.Pixel(13, 13),
                            size: new AMap.Size(25, 25)
                            }, 
                            {
                            url: 'icons/lightbrown_tennisball.png',
                            anchor: new AMap.Pixel(13, 13),
                            size: new AMap.Size(25, 25)
                            }, 
                            {
                            url: 'icons/purple_moon.png',
                            anchor: new AMap.Pixel(13, 13),
                            size: new AMap.Size(25, 25)
                            }, 
                            {
                            url: 'icons/blue_bubble.png',
                            anchor: new AMap.Pixel(16, 16),
                            size: new AMap.Size(25, 25)
                            }
                        ];

            var citys = [
            '''
        self.suffix = '''
            ];
            var mass = new AMap.MassMarks(citys, {
                    opacity:1,
                    zIndex: 111,
                    cursor:'pointer',
                    style:style
            });
            var marker = new AMap.Marker({content:' ',map:map})
            mass.on('mouseover',function(e){
                marker.setPosition(e.data.lnglat);
                marker.setLabel({content:e.data.name})
            })
            mass.setMap(map);
            </script>
        </body>
        </html>
        '''

    def add_nodes(self, nodes, labels=None, style=3):
        nnodes = len(nodes)
        items = []
        for i in range(nnodes):
            if type(nodes[i][0]) == type(1.0):
                coords = '[%f,%f]' % (nodes[i][0], nodes[i][1])
            else:
                coords = '[%s,%s]' % (nodes[i][0], nodes[i][1])
            if labels is None:
                label = coords
            else:
                label = labels[i]
            item = "{\"lnglat\":%s,\"name\":\"%s\",\"style\":%d}" % (coords, label, style)
            items.append(item)

        self.add_count += 1
        if self.add_count > 1:
            self.prefix += ","
        self.prefix += ",\n".join(items) 
        return self

    def render(self):
        with open(self.fname + ".html", "w") as f:
            f.write(self.prefix + self.suffix)

def test_MapDotter():
    md = MapDotter("lac")
    nodes = []
    for line in open("4238.csv"):
        [lon, lat] = line.strip().split("\t")
        nodes.append([lon, lat])
    md.add_nodes(nodes)
    md.render()

def test_haversine():        
    print(haversine(lng1, lat1, lng1-0.001, lat1))
    print(haversine(lng1, lat1, lng1, lat1+0.001))
    print(haversine(116.348114, 40.03619, 116.38785, 39.94561))

def test_coors_conversion():
    lng = 128.543
    lat = 37.065
    result1 = gcj02_to_bd09(lng, lat)
    result2 = bd09_to_gcj02(lng, lat)
    result3 = wgs84_to_gcj02(lng, lat)
    result4 = gcj02_to_wgs84(lng, lat)
    result5 = bd09_to_wgs84(lng, lat)
    result6 = wgs84_to_bd09(lng, lat)

def mapDotterTool(fname):
    labels = []
    nodes = []
    oldstyle = -1
    md = MapDotter(fname)
    for line in open(fname):
        parts = line.strip().split(',')
        if len(parts) != 4: continue
        lon, lat, label, style = parts[0], parts[1], parts[2], parts[3]
        if not lon[:2].isnumeric(): continue
        style = int(float(style))
        nstyle = 8
        style %= nstyle
        if style != oldstyle:
            if nodes != []:
                md.add_nodes(nodes, labels, oldstyle)
                labels = []
                nodes = []
                
        labels.append(label)
        nodes.append([float(lon), float(lat)])
        oldstyle = style
    
    if nodes != []:
        md.add_nodes(nodes, labels, oldstyle)
    md.render()
        

attern1 = re.compile('[^\.\d](\d{1,3}\.\d{1,})[^\.\d]{1,12}(\d{1,3}\.\d{1,})([^\.\d]|$)')
pattern2 = re.compile('[^\.\d](\d{1,3}\.\d{1,})[^\.\d]{1,3}\d[^\.\d]{1,3}(\d{1,3}\.\d{1,})([^\.\d]|$)')
pattern_single = re.compile('[^\.\d](\d{1,3}\.\d{1,})([^\.\d]|$)')

# 在URL中提取经纬度
def findlonlat2(url):
    m = pattern1.search(url, 0)
    if m is not None:
        clon = float(m.group(1))
        clat = float(m.group(2))
        if clon < clat:
            clon, clat = clat, clon
        if clon > 73.6 and clon < 135.1 and clat > 3.86 and clat < 53.55: return (clon, clat)
        
    m = pattern2.search(url, 0)
    if m is not None:
        clon = float(m.group(1))
        clat = float(m.group(2))
        if clon < clat:
            clon, clat = clat, clon
        if clon > 73.6 and clon < 135.1 and clat > 3.86 and clat < 53.55: return (clon, clat)
    
    lon = 0
    lat = 0
    m = pattern_single.search(url, 0)
    while m is not None:
        mv = float(m.group(1))
        if mv > 73.6 and mv < 135.1:
            lon = mv
        elif mv > 3.86 and mv < 53.55:
            lat = mv
        m = pattern_single.search(url, m.end(1))
    if lat == 0 or lon == 0: return (0, 0)
    return (lon, lat)

# 判断某点p3是否在线段(p1,p2)上
def point_in_segment(p3, p1, p2):
    if (p3[0]-p1[0]) * (p2[1]-p3[1]) == (p3[1]-p1[1]) * (p2[0]-p3[0]):#p1,p2,p3共线
        xmin = min(p1[0], p2[0])
        xmax = max(p1[0], p2[0])
        return p3[0] >= xmin and p3[0] <= xmax # x1 <= x3 <= x2
    return False


#判断线段(p1,p2)与(p3,p4)是否真正相交
def segment_cross(p1,p2,p3,p4):
    if point_in_segment(p3, p1, p2) or point_in_segment(p4, p1, p2):
        return True
    
    if p1[0] == p2[0]: #(p1,p2)为垂直线段:x1==x2
        if p1[1] > p2[1]: p1, p2 = p2, p1 #不失一般性，要求y1 <= y2
        if p3[1] > p4[1]: p3, p4 = p4, p3 #不失一般性，要求y3 <= y4

        x = p1[0]
        y = ((p4[0]-x)*p3[1] + (x - p3[0])*p4[1]) * 1.0 / (p4[0]-p3[0])
        return y >= p1[1] and y <= p2[1] and y >= p3[1] and y <= p4[1]
    
    if p1[0] > p2[0]: p1, p2 = p2, p1 #不失一般性，要求 x1 <= x2
    if p3[0] > p4[0]: p3, p4 = p4, p3

    t1 = (p2[1]-p1[1])*1.0/(p2[0]-p1[0])
    t2 = (p2[0]*p1[1] - p1[0]*p2[1])*1.0/(p2[0]-p1[0])
    t3 = (p4[1]-p3[1])*1.0/(p4[0]-p3[0])
    t4 = (p4[0]*p3[1] - p3[0]*p4[1])*1.0/(p4[0]-p3[0])
    if t1 == t3: #平行
        return False
    x= (t4-t2)/(t1-t3)
    #y= t1 * x + t2 = t3 * x+t4
    if x < p1[0] or x > p2[0]: return False
    if x < p3[0] or x > p4[0]: return False
    return True

# 获得点集合的矩形轮廓: 左下，右上
def get_range(points):
    xlist,ylist = (zip(*points))
    return min(xlist), min(ylist), max(xlist), max(ylist)
    
# 获得点集合两两构成的线段
def get_segments(points):
    segments = []
    for i, p in enumerate(points[:-1]):
        segment = (p, points[i+1])
        segments.append(segment)
    segments.append((points[-1], points[0]))
    return segments

# 判断某点pcheck是否在某点集points两两连接构成的图形内
def point_in_area(pcheck, points):
    xmin, ymin, xmax, ymax = get_range(points)
    if pcheck[0] < xmin or pcheck[0] > xmax or pcheck[1] < ymin or pcheck[1] > ymax: 
        return False #不在平直矩形轮廓内的，一定不在图形内
    
    #选择一个很大的点pmax，构造线段(pcheck, pmax)
    pmax = (xmax+1, ymax+1)
    ncross = 0 #交点数
    for segment in get_segments(points):
        p1, p2 = segment
        if point_in_segment(pcheck, p1, p2): return True
        print (segment, pmax, segment_cross(p1, p2, pcheck, pmax))
        if segment_cross(p1, p2, pcheck, pmax):
            ncross += 1
    return ncross % 2 == 1 #交点数为奇数


if __name__ == '__main__':
    if len(sys.argv) >= 3:
        command = sys.argv[1]
        subpara = sys.argv[2]
        if command == "amap":
            mapDotterTool(subpara)





