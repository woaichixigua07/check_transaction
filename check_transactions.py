#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import requests
import datetime
import xlrd
import xlwt
from xlutils.copy import copy
from tronapi import Tron
import math
import operator

# tronscan 查询余额地址           
usdt_info_from_tronscan_url = "https://apilist.tronscan.org/api/token_trc20/holders?sort=-balance&start="
# 合约地址
contract_address = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t" 

# add browser headers
headers={
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'Cookie':'__cfduid=da90fabee5f4d96a316a104f96f0476bd1552904746; gtm_session_first=Mon%20Mar%2018%202019%2018:24:58%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4); _ga=GA1.2.1809757759.1552904698; _gid=GA1.2.1536504574.1552904698; _fbp=fb.1.1552904698688.846897282; __gads=ID=df0e159e39a6f1bc:T=1552904750:S=ALNI_Mb2GRbqU9zQCWB8Lc_nA4QIsEBTjw; cmc_gdpr_hide=1; gtm_session_last=Mon%20Mar%2018%202019%2020:24:30%20GMT+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4); _awl=2.1552911928.0.4-68ecec8c-3d6c2c480ef438cc86a4fd41099005f0-6763652d75732d7765737431-5c8f8e38-0'
}

# tron sets
full_node = 'https://api.trongrid.io'
solidity_node = 'https://api.trongrid.io'
event_server = 'https://api.trongrid.io'

tron = Tron(full_node=full_node,
        solidity_node=solidity_node,
        event_server=event_server)

def check_transactions(address,excel_path):
    base_url = "https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=20&start="+str(0)+"&address="
    transactions_info_tronscan_s = requests.get(base_url+address,headers=headers,timeout=30)


    if transactions_info_tronscan_s.status_code == 200:
        transactions_info_tronscan = requests.get(base_url+address,headers=headers,timeout=30).json()
        transactions_total = transactions_info_tronscan['total']
        for i in range(math.floor(transactions_total/20)):
            url_new = "https://apilist.tronscan.org/api/transaction?sort=-timestamp&count=true&limit=20&start="+str(math.floor(transactions_total/20)*20)+"&address="
            transactions_info_tronscan_s = requests.get(base_url+address,headers=headers,timeout=30)
            if transactions_info_tronscan_s.status_code == 200:
                transactions_list_tronscan = transactions_info_tronscan_s.json()['data']
                for data_num in range(len(transactions_list_tronscan)):
                    txid = transactions_list_tronscan[data_num]['hash']
                    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # 获取当前时间
                    #print('txid:', txid)
                    tran_info_from_trongrid = get_transactions_from_trongrid(txid)
                    tran_info_from_tronscan = get_transactions_from_tronscan(txid)
                    if  tran_info_from_trongrid == None:
                        tran_info_from_trongrid = []
                    if  tran_info_from_tronscan == None:
                        tran_info_from_tronscan = []

                    if len(tran_info_from_trongrid) > 0 or len(tran_info_from_tronscan) > 0:
                    #if len(tran_info_from_trongrid) != len(tran_info_from_tronscan):
 
                        if len(tran_info_from_trongrid) == len(tran_info_from_tronscan):
                            txid_all_list  = [txid_all for txid_all in tran_info_from_trongrid if txid_all in tran_info_from_tronscan ]
                            diff = [diff_txid for diff_txid in (tran_info_from_trongrid + tran_info_from_tronscan) if diff_txid not in txid_all_list]
                            if len(diff) > 0:
                                print("==============Trongrid & Tronscan数据不一致===================") 
                                value = [[address,txid,tran_info_from_trongrid,tran_info_from_tronscan,time],]
                                write_diff_trc20token_info_to_excel(excel_path,value) 
                        else:
                            print("==============Trongrid & Tronscan数据不一致===================") 
                            value = [[address,txid,tran_info_from_trongrid,tran_info_from_tronscan,time],]
                            write_diff_trc20token_info_to_excel(excel_path,value) 

                           
    else:
        get_transactions_from_tronscan(address)
        
def get_transactions_from_trongrid(txid):

    base_url_trongrid = 'https://api.trongrid.io/wallet/gettransactioninfobyid?value='
    transactions_info_trongrid_s = requests.get(base_url_trongrid+txid,headers=headers,timeout=30)   
    if transactions_info_trongrid_s.status_code == 200:
        print('from trongrid',transactions_info_trongrid_s)
        transactions_info_trongrid = transactions_info_trongrid_s.json()
        if 'internal_transactions' in transactions_info_trongrid:
            if len(transactions_info_trongrid['internal_transactions']) >0 :
                trongrid_internal_tran_len = len(transactions_info_trongrid['internal_transactions'])
                trongrid_internal_tran_list = [transactions_info_trongrid['internal_transactions'][i]['hash'] for i in range(trongrid_internal_tran_len) ] 
            else:
                trongrid_internal_tran_len =0
                trongrid_internal_tran_list = []
            return trongrid_internal_tran_list
        else:
            trongrid_internal_tran_list = []
            return trongrid_internal_tran_list
    else:
        get_transactions_from_trongrid(txid)


def get_transactions_from_tronscan(txid):
    base_url_tronscan = 'https://apilist.tronscan.org/api/transaction-info?hash='
    transactions_info_tronscan_s = requests.get(base_url_tronscan+txid,headers=headers,timeout=30)
    if transactions_info_tronscan_s.status_code == 200:
        print('from tronscan',transactions_info_tronscan_s,transactions_info_tronscan_s.content)
        transactions_info_tronscan = transactions_info_tronscan_s.json()
        if len(transactions_info_tronscan['internal_transactions']) >0 :
            tronscan_internal_tran_len = len(transactions_info_tronscan['internal_transactions']['1'])
            tronscan_internal_tran_list = [transactions_info_tronscan['internal_transactions']['1'][i]['hash'] for i in range(tronscan_internal_tran_len) ]
        else:
            tronscan_internal_tran_len =0
            tronscan_internal_tran_list = []
        return tronscan_internal_tran_list
    else:
        get_transactions_from_tronscan(txid)


# get usdt info from tronscan
def check_address_info_from_tronscan(tronscan_url,excel_path):
    usdt_info_form_tronscan_content1 = requests.get(tronscan_url,headers=headers,timeout=30)
    usdt_info_form_tronscan_content = usdt_info_form_tronscan_content1.json() # 获取tronscan 上USDT部分holder的余额信息

    if usdt_info_form_tronscan_content1.status_code == 200:
        for i in range(len(usdt_info_form_tronscan_content['trc20_tokens'])):
            address = usdt_info_form_tronscan_content['trc20_tokens'][i]['holder_address'] # 获取holders address  
            check_transactions(address,excel_path)          
    else:
        check_address_info_from_tronscan(tronscan_url,excel_path)
    return 

def create_excel_xls(path, sheet_name, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(sheet_name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.write(i, j, value[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿
    print("xls格式表格初始化数据成功！")

def write_diff_trc20token_info_to_excel(path, value):
    index = len(value)  # 获取需要写入数据的行数
    workbook = xlrd.open_workbook(path)  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格
    worksheet = workbook.sheet_by_name(sheets[0])  # 获取工作簿中所有表格中的的第一个表格
    rows_old = worksheet.nrows  # 获取表格中已存在的数据的行数
    new_workbook = copy(workbook)  # 将xlrd对象拷贝转化为xlwt对象
    new_worksheet = new_workbook.get_sheet(0)  # 获取转化后工作簿中的第一个表格
    for i in range(0, index):
        for j in range(0, len(value[i])):
            new_worksheet.write(i+rows_old, j, value[i][j])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
    print("xls格式表格【追加】写入数据成功！")


def main():

    #--------------
    # 初始化excel表
    #--------------
    path = "/Users/tron/Desktop/tran_check/tran_check_0422.xls" # excel表路径
    sheet_name = "usdt_balance_diff_check" 
    value_title = [["address", "txid", "tran_info_from_trongrid","tran_info_from_tronscan","check_time"],]
    create_excel_xls(path,sheet_name,value_title)
    #--------------
    # 对比余额是否相等
    #--------------
    start_num = 20
    for i in range(0,500):    
        try:
            print("********************第" + str(i+1) + "页********************")
            tronscan_url = usdt_info_from_tronscan_url + str(i*start_num) + "&limit=20" + "&contract_address=" + contract_address
            check_address_info_from_tronscan(tronscan_url,path)
        except Exception as a:
            print("********************第" + str(i+1) + "页********************")
            tronscan_url = usdt_info_from_tronscan_url + str(i*start_num) + "&limit=20" + "&contract_address=" + contract_address
            check_address_info_from_tronscan(tronscan_url,path)

    print("-----CHECK DONE!!!-----")

if (__name__ == "__main__"):

    main()
    #get_transactions_from_tronscan("TMuA6YqfCeX8EhbfYEg5y7S4DqzSJireY9")
    #get_trc20token_balanceOf_from_trongridV1("TQc1yCwBn9FQ94N1SdEavqjPE4YtSATi6a")

    #get_transactions_from_trongrid1 = get_transactions_from_trongrid('ad7cab01c604f33d51dfb5103fa178d08d3a94bed36c686fbf0cb4e68e776c7e')
    #print(len(get_transactions_from_trongrid1))
    #tran_info_from_trongrid1 = get_transactions_from_trongrid('ad7cab01c604f33d51dfb5103fa178d08d3a94bed36c686fbf0cb4e68e776c7e')
    #print(len(tran_info_from_trongrid1))
    #if len(tran_info_from_trongrid) != len(tran_info_from_tronscan):
    #    print("fff")
    #a = [x for x in tran_info_from_tronscan if x in tran_info_from_trongrid]
    #print(a)
