# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import settings
import model
import misc
import time
import datetime
import urllib
import logger

msg = "这是个测试文本"
logger.error("xxxxx %s"  % msg)
logger.warning("xxxxx %s"  % msg)
logger.info("xxxxx %s"  % msg)
logger.debug("xxxxx %s"  % msg)

#
# https://hz.lianjia.com/ershoufang/xihu/
#
BASE_URL = u"http://%s.lianjia.com/" % (settings.CITY)
CITY = settings.CITY

def GetHouseByCommunitylist(communitylist):
    logger.info("Get House Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_house_percommunity(community)
        except Exception as e:
            logger.error(e)
            logger.error(community + "Fail")
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def GetSellByCommunitylist(communitylist):
    logger.info("Get Sell Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_sell_percommunity(community)
        except Exception as e:
            logger.error(e)
            logger.error(community + "Fail")
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def GetRentByCommunitylist(communitylist):
    logger.info("Get Rent Infomation")
    starttime = datetime.datetime.now()
    for community in communitylist:
        try:
            get_rent_percommunity(community)
        except Exception as e:
            logger.error(e)
            logger.error(community + "Fail")
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def GetCommunityByRegionlist(regionlist=[u'xicheng']):
    logger.info("Get Community Infomation")
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        try:
            get_community_perregion(regionname)
            logger.info(regionname + "Done")
        except Exception as e:
            logger.error(e)
            logger.error(regionname + "Fail")
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def GetHouseByRegionlist(regionlist=[u'xihu']):
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logger.info("Get Onsale House Infomation in %s" % regionname)
        try:
            get_house_perregion(regionname)
        except Exception as e:
            logger.error(e)
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def GetRentByRegionlist(regionlist=[u'xicheng']):
    starttime = datetime.datetime.now()
    for regionname in regionlist:
        logger.info("Get Rent House Infomation in %s" % regionname)
        try:
            get_rent_perregion(regionname)
        except Exception as e:
            logger.error(e)
            pass
    endtime = datetime.datetime.now()
    logger.info("Run time: " + str(endtime - starttime))

def get_house_percommunity(communityname):
    url = BASE_URL + u"ershoufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    
    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class":"clear"})
        i = 0
        log_progress("GetHouseByCommunitylist", communityname, page+1, total_pages)
        houseinfo_data_source = []
        houseprice_data_source = []
        for name in nameList: # per house loop
            i = i + 1
            info_dict = {}
            try:
                housetitle = name.find("div", {"class":"title"})
                info_dict.update({u'title':housetitle.a.get_text().strip()})
                info_dict.update({u'link':housetitle.a.get('href')})

                houseaddr = name.find("div", {"class":"address"})
                if CITY == 'bj':
                    info = houseaddr.div.get_text().split('/')
                else:
                    info = houseaddr.div.get_text().split('|')
                info_dict.update({u'community':info[0].strip()})
                info_dict.update({u'housetype':info[1].strip()})
                info_dict.update({u'square':info[2].strip()})
                info_dict.update({u'direction':info[3].strip()})
                info_dict.update({u'decoration':info[4].strip()})

                housefloor = name.find("div", {"class":"flood"})
                floor_all = housefloor.div.get_text().split('-')[0].strip().split(' ')
                info_dict.update({u'floor':floor_all[0].strip()})
                info_dict.update({u'years':floor_all[-1].strip()})

                followInfo = name.find("div", {"class":"followInfo"})
                info_dict.update({u'followInfo':followInfo.get_text()})

                tax = name.find("div", {"class":"tag"})
                info_dict.update({u'taxtype':tax.get_text().strip()})

                totalPrice = name.find("div", {"class":"totalPrice"})
                info_dict.update({u'totalPrice':totalPrice.span.get_text()})

                unitPrice = name.find("div", {"class":"unitPrice"})
                info_dict.update({u'unitPrice':unitPrice.get('data-price')})
                info_dict.update({u'id':unitPrice.get('data-hid')})
            except:
                continue

            # houseinfo insert into mysql
            houseinfo_data_source.append(info_dict)
            logger.info("----------------------------------------------------------------------")
            logger.info(info_dict)
            houseprice_data_source.append({"id":info_dict["id"], "totalPrice":info_dict["totalPrice"]})

        with model.database.atomic():
            model.Houseinfo.insert_many(houseinfo_data_source).on_conflict_replace().execute()
            model.Houseprice.insert_many(houseprice_data_source).on_conflict_replace().execute()
        time.sleep(1)

def get_sell_percommunity(communityname):
    url = BASE_URL + u"chengjiao/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    
    if total_pages == None:
        row = model.Sellinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"chengjiao/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetSellByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"listContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    id = housetitle.a.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'id':id.strip()})

                    house = housetitle.get_text().strip().split(' ')
                    info_dict.update({u'community':house[0].strip()})
                    info_dict.update({u'housetype':house[1].strip()})
                    info_dict.update({u'square':house[2].strip()})

                    houseinfo = name.find("div", {"class":"houseInfo"})
                    info = houseinfo.get_text().split('|')
                    info_dict.update({u'direction':info[0].strip()})
                    info_dict.update({u'status':info[1].strip()})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    floor_all = housefloor.get_text().strip().split(' ')
                    info_dict.update({u'floor':floor_all[0].strip()})
                    info_dict.update({u'years':floor_all[-1].strip()})

                    followInfo = name.find("div", {"class":"source"})
                    info_dict.update({u'source':followInfo.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    if totalPrice.span is None:
                        info_dict.update({u'totalPrice':totalPrice.get_text().strip()})
                    else:
                        info_dict.update({u'totalPrice':totalPrice.span.get_text().strip()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    if unitPrice.span is None:
                        info_dict.update({u'unitPrice':unitPrice.get_text().strip()})
                    else:
                        info_dict.update({u'unitPrice':unitPrice.span.get_text().strip()})

                    dealDate= name.find("div", {"class":"dealDate"})
                    info_dict.update({u'dealdate':dealDate.get_text().strip().replace('.','-')})

                except:
                    continue
                # Sellinfo insert into mysql
                data_source.append(info_dict)
                #model.Sellinfo.insert(**info_dict).on_conflict_replace().execute()

        with model.database.atomic():
            model.Sellinfo.insert_many(data_source).on_conflict_replace().execute()
        time.sleep(1)

def get_community_perregion(regionname=u'xicheng'):
    url = BASE_URL + u"xiaoqu/" + regionname +"/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    
    if total_pages == None:
        row = model.Community.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"xiaoqu/" + regionname +"/pg%d/" % page
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')

        nameList = soup.findAll("li", {"class":"clear"})
        i = 0
        log_progress("GetCommunityByRegionlist", regionname, page+1, total_pages)
        data_source = []
        for name in nameList: # Per house loop
            i = i + 1
            info_dict = {}
            try:
                communitytitle = name.find("div", {"class":"title"})
                title = communitytitle.get_text().strip('\n')
                link = communitytitle.a.get('href')
                info_dict.update({u'title':title})
                info_dict.update({u'link':link})

                district = name.find("a", {"class":"district"})
                info_dict.update({u'district':district.get_text()})
                
                bizcircle = name.find("a", {"class":"bizcircle"})
                info_dict.update({u'bizcircle':bizcircle.get_text()})

                tagList = name.find("div", {"class":"tagList"})
                info_dict.update({u'tagList':tagList.get_text().strip('\n')})

                onsale = name.find("a", {"class":"totalSellCount"})
                info_dict.update({u'onsale':onsale.span.get_text().strip('\n')})

                onrent = name.find("a", {"title":title+u"租房"})
                info_dict.update({u'onrent':onrent.get_text().strip('\n').split(u'套')[0]})

                info_dict.update({u'id':name.get('data-housecode')})

                price = name.find("div", {"class":"totalPrice"})
                info_dict.update({u'price':price.span.get_text().strip('\n')})


                communityinfo = get_communityinfo_by_url(link)
                for key, value in communityinfo.iteritems():
                    info_dict.update({key:value})

            except:
                continue
            # communityinfo insert into mysql
            data_source.append(info_dict)
            #model.Community.insert(**info_dict).on_conflict_replace().execute()

        with model.database.atomic():
            model.Community.insert_many(data_source).on_conflict_replace().execute()
        time.sleep(1)

def get_rent_percommunity(communityname):
    url = BASE_URL + u"zufang/rs" + urllib.request.quote(communityname.encode('utf8')) + "/"
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)

    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"rent/pg%drs%s/" % (page, urllib.request.quote(communityname.encode('utf8')))
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByCommunitylist", communityname, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"info-panel"})
                    info_dict.update({u'title':housetitle.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    id = housetitle.a.get('href').split("/")[-1].split(".")[0]
                    info_dict.update({u'id':id})

                    region = name.find("span", {"class":"region"})
                    info_dict.update({u'region':region.get_text().strip()})

                    zone = name.find("span", {"class":"zone"})
                    info_dict.update({u'zone':zone.get_text().strip()})

                    meters = name.find("span", {"class":"meters"})
                    info_dict.update({u'meters':meters.get_text().strip()})

                    other = name.find("div", {"class":"con"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("span", {"class":"fang-subway-ex"})
                    if subway is None:
                        info_dict.update({u'subway':""})
                    else:
                        info_dict.update({u'subway':subway.span.get_text().strip()})

                    decoration = name.find("span", {"class":"decoration-ex"})
                    if decoration is None:
                        info_dict.update({u'decoration':""})
                    else:
                        info_dict.update({u'decoration':decoration.span.get_text().strip()})

                    heating = name.find("span", {"class":"heating-ex"})
                    info_dict.update({u'heating':heating.span.get_text().strip()})

                    price = name.find("div", {"class":"price"})
                    info_dict.update({u'price':int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class":"price-pre"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).on_conflict_replace().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).on_conflict_replace().execute()
        time.sleep(1)

def get_house_perregion(district):
    url = BASE_URL + u"ershoufang/%s/" % district
    logger.info(url)
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return

    total_pages = misc.get_total_pages(url)
    if total_pages == None:
        row = model.Houseinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"ershoufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetHouseByRegionlist", district, page+1, total_pages)
        houseinfo_data_source = []
        houseprice_data_source = []
        for ultag in soup.findAll("ul", {"class":"sellListContent"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"title"})
                    info_dict.update({u'title':housetitle.a.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get('href')})
                    id = housetitle.a.get('data-housecode')
                    info_dict.update({u'id':id})


                    houseinfo = name.find("div", {"class":"houseInfo"})
                    if CITY == 'bj':
                        info = houseinfo.get_text().split('/')
                    else:
                        info = houseinfo.get_text().split('|')
                    info_dict.update({u'community':info[0]})
                    info_dict.update({u'housetype':info[1]})
                    info_dict.update({u'square':info[2]})
                    info_dict.update({u'direction':info[3]})
                    info_dict.update({u'decoration':info[4]})

                    housefloor = name.find("div", {"class":"positionInfo"})
                    info_dict.update({u'years':housefloor.get_text().strip()})
                    info_dict.update({u'floor':housefloor.get_text().strip()})

                    followInfo = name.find("div", {"class":"followInfo"})
                    info_dict.update({u'followInfo':followInfo.get_text().strip()})

                    taxfree = name.find("span", {"class":"taxfree"})
                    if taxfree == None:
                        info_dict.update({u"taxtype":""})
                    else:
                        info_dict.update({u"taxtype":taxfree.get_text().strip()})

                    totalPrice = name.find("div", {"class":"totalPrice"})
                    info_dict.update({u'totalPrice':totalPrice.span.get_text()})

                    unitPrice = name.find("div", {"class":"unitPrice"})
                    info_dict.update({u'unitPrice':unitPrice.get("data-price")})
                except:
                    continue

                # Houseinfo insert into mysql
                houseinfo_data_source.append(info_dict)
                logger.info("----------------------------------------------------------------------")
                logger.info(info_dict)
                houseprice_data_source.append({"id":info_dict["id"], "totalPrice":info_dict["totalPrice"]})

        with model.database.atomic():
            model.Houseinfo.insert_many(houseinfo_data_source).on_conflict_replace().execute()
            model.Houseprice.insert_many(houseprice_data_source).on_conflict_replace().execute()
        time.sleep(1)


def get_rent_perregion(district):
    url = BASE_URL + u"zufang/%s/" % district
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')
    if check_block(soup):
        return
    total_pages = misc.get_total_pages(url)
    if total_pages == None:
        row = model.Rentinfo.select().count()
        raise RuntimeError("Finish at %s because total_pages is None" % row)

    for page in range(total_pages):
        if page > 0:
            url_page = BASE_URL + u"zufang/%s/pg%d/" % (district, page)
            source_code = misc.get_source_code(url_page)
            soup = BeautifulSoup(source_code, 'lxml')
        i = 0
        log_progress("GetRentByRegionlist", district, page+1, total_pages)
        data_source = []
        for ultag in soup.findAll("ul", {"class":"house-lst"}):
            for name in ultag.find_all('li'):
                i = i + 1
                info_dict = {}
                try:
                    housetitle = name.find("div", {"class":"info-panel"})
                    info_dict.update({u'title':housetitle.h2.a.get_text().strip()})
                    info_dict.update({u'link':housetitle.a.get("href")})
                    id = name.get("data-housecode")
                    info_dict.update({u'id':id})

                    region = name.find("span", {"class":"region"})
                    info_dict.update({u'region':region.get_text().strip()})

                    zone = name.find("span", {"class":"zone"})
                    info_dict.update({u'zone':zone.get_text().strip()})

                    meters = name.find("span", {"class":"meters"})
                    info_dict.update({u'meters':meters.get_text().strip()})

                    other = name.find("div", {"class":"con"})
                    info_dict.update({u'other':other.get_text().strip()})

                    subway = name.find("span", {"class":"fang-subway-ex"})
                    if subway == None:
                        info_dict.update({u'subway':""})
                    else:
                        info_dict.update({u'subway':subway.span.get_text().strip()})

                    decoration = name.find("span", {"class":"decoration-ex"})
                    if decoration == None:
                        info_dict.update({u'decoration': ""})
                    else:
                        info_dict.update({u'decoration':decoration.span.get_text().strip()})

                    heating = name.find("span", {"class":"heating-ex"})
                    if decoration == None:
                        info_dict.update({u'heating': ""})
                    else:
                        info_dict.update({u'heating':heating.span.get_text().strip()})

                    price = name.find("div", {"class":"price"})
                    info_dict.update({u'price':int(price.span.get_text().strip())})

                    pricepre = name.find("div", {"class":"price-pre"})
                    info_dict.update({u'pricepre':pricepre.get_text().strip()})

                except:
                    continue
                # Rentinfo insert into mysql
                data_source.append(info_dict)
                #model.Rentinfo.insert(**info_dict).on_conflict_replace().execute()

        with model.database.atomic():
            model.Rentinfo.insert_many(data_source).on_conflict_replace().execute()
        time.sleep(1)

def get_communityinfo_by_url(url):
    source_code = misc.get_source_code(url)
    soup = BeautifulSoup(source_code, 'lxml')

    if check_block(soup):
        return

    communityinfos = soup.findAll("div", {"class":"xiaoquInfoItem"})
    res = {}
    for info in communityinfos:
        key_type = {
        u"建筑年代": u'year',
        u"建筑类型": u'housetype',
        u"物业费用": u'cost',
        u"物业公司": u'service',
        u"开发商": u'company',
        u"楼栋总数": u'building_num',
        u"房屋总数": u'house_num',
        }
        try:
            key = info.find("span",{"xiaoquInfoLabel"})
            value = info.find("span",{"xiaoquInfoContent"})
            key_info = key_type[key.get_text().strip()]
            value_info = value.get_text().strip()
            res.update({key_info:value_info})

        except:
            continue
    return res

def check_block(soup):
    if soup.title.string == "414 Request-URI Too Large":
        logger.error("Lianjia block your ip, please verify captcha manually at lianjia.com")
        return True
    return False

def log_progress(function, address, page, total):
    logger.info("Progress: %s %s: current page %d total pages %d" %(function, address, page, total))
