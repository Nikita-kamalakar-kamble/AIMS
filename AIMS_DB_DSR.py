# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 11:22:21 2023

@author: nikita.kamble


"""

import cx_Oracle
import pandas as pd
import numpy as np
from datetime import date, timedelta
import openpyxl

try:
    cx_Oracle.init_oracle_client(lib_dir=r"C:\Users\Nikita.Kamble\Downloads\instantclient-basic-windows.x64-21.9.0.0.0dbru\instantclient_21_9")
except:
    pass
#=================Variable Initialization =============
Path= r"C:\Users\Nikita.Kamble\OneDrive - M.H. Alshaya Co. W.L.L\Desktop\DSR Wholesale\AIMS"
Script_Path = r"C:\Users\Nikita.Kamble\OneDrive - M.H. Alshaya Co. W.L.L\Desktop\DSR Wholesale\AIMS\AIMS Query.sql"
output_file = r"C:\Users\Nikita.Kamble\OneDrive - M.H. Alshaya Co. W.L.L\Desktop\DSR Wholesale\AIMS\AIMS_Reco.xlsx"
mapping_file = r"C:\Users\Nikita.Kamble\OneDrive - M.H. Alshaya Co. W.L.L\Desktop\DSR Wholesale\AIMS\mapping file.xlsx"
rows=[] 

#=================Read discoverer downloaded sheet and paste in output file =============
def oracle_sheet_prep():
    OracleDiscovererFile = Path + "\Oracle_Data_26062023.xls"
    # wb = openpyxl.load_workbook(OracleDiscovererFile)
    # sheet = wb.active
    # data = []
    # for row in sheet.iter_rows(values_only=True):
    #     data.append(row)
    print("reading execl")
    disc_df = pd.read_excel(OracleDiscovererFile)
    print("completed")
    #df2 = disc_df.iloc[7:,:]
    df2 = disc_df.loc[:, disc_df.notnull().any(axis=0)]
    # df2 = pd.DataFrame(data)
    df2.columns = ['Trx Date','Trx Number','Site Name','Amount','Balance']
# print(df2.shape)
# print(df2.head)
    #df2.to_excel(output_file,"Oracle Data",index=False)
    return df2

#=================Date logic to test later=============

def generateDate():
    today = date.today()
    cutoff = 15
    if today.day < 15:
        start_date = today - timedelta(days=cutoff)
        end_date = today
    elif today.day >= 15:
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 30)
    return [start_date,end_date]





def DowbloadAIMSData(ReportType):
    #hostname = "172.16.100.240" #hostname for Food divison #port 1531 #service AIMSFOOD #user="aims", password="aims"
    if ReportType == "Food":
        dsnStr = cx_Oracle.makedsn("172.16.100.240", "1531", "AIMSFOOD")
        con = cx_Oracle.connect(user="aims", password="aims", dsn = dsnStr )    
        cur = con.cursor() 
        with open(Script_Path,'r') as script:
            query = script.read()
            cur.execute(query)
            rows = cur.fetchall()
        con.close()
        return rows
    #hostname = "172.16.100.66" #hostname for NonFood divison'aimsdb''paragj''par18ja23'.1521
    if ReportType == "NonFood":
        dsnStr = cx_Oracle.makedsn("172.16.100.66", "1521", "aimsdb")
        con = cx_Oracle.connect(user="paragj", password="par18ja25", dsn = dsnStr )    
        cur = con.cursor() 
        with open(Script_Path,'r') as script:
            query = script.read()
            cur.execute(query)
            rows = cur.fetchall()
        con.close()
        return rows
    
 

print("execution start")       
#========================Code sequence===========================
dates = generateDate()
rows = DowbloadAIMSData("NonFood")
df = pd.DataFrame(rows, columns =['Brand Code','Brand Name','Entity Code','Entity Name','Invoice No','Invoice Date','Customer','Customer Name','Customer Site','Customer Site Name','Currency','Invoice Amount','Article Code','Article Description','Article Note','Article Amount','VAT Percent','VAT Collected','Status','Remark','Shipment_ref','Credit Note','CreatedOn','CreatedBy','CancelledBy','CancelledOn','Reason for Cancellation'])
map_df = pd.read_excel(mapping_file,"VAT%")

print(dates[0],dates[1])
#Unable this code in production
df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%Y-%m-%d')
df2 = df.loc[(df['Invoice Date'].dt.date >= dates[0]) & (df['Invoice Date'].dt.date <= dates[1])]  
# print(df.shape)
# print(df2.shape)
df = df.loc[(df['Invoice Date'].dt.date >= dates[0]) & (df['Invoice Date'].dt.date <= dates[1])]  
df = df.merge(map_df, how = "left",left_on = "Entity Code", right_on = "Entity")
df['VAT VAlidation'] = np.where((df['Entity Code'] == df['Entity']), ' Matching','Not Matching')
#steps to filter for unique invoice numbers and prepare reco sheet
print("Aims datadownloaded")

ora_df = oracle_sheet_prep()

OracleDF = ora_df.loc[:,['Trx Number','Amount']]

AimsDF = df2.loc[:,['Entity Code','Entity Name','Invoice No','Invoice Date','Invoice Amount']]


df3 = AimsDF.groupby(['Invoice No','Entity Code','Entity Name'])['Invoice Amount'].sum()
dff = df3.to_frame()
dff.reset_index(inplace = True)


df4 = dff.merge(OracleDF, how = "left",left_on = "Invoice No", right_on = "Trx Number")

df4['Variance'] = df4['Invoice Amount'].round() - df4['Amount'].round()



#df4['status'] = np.where(((df4['Variance'] < 0)&(df4['Variance'] > 0)), 'Business Exception',' ')

#df4['OracleStatus'] = np.where(df4['Amount'].isnull(), 'Oracle Data not found',' ')
#df4['status'] = np.where((df4['Variance'] == 0), 'Matching','Business Exception')
df4['status'] = np.where((df4['Variance'] != 0),np.where((df4['Variance'].isnull()),'Oracle Data Not available','Business exception'),'Matching')
Reco = df4.loc[:,['Invoice No','Entity Code','Entity Name','Invoice Amount','Amount','Variance','status']]
Reco.columns = ['Invoice No','Entity Code','Entity Name','Invoice Amount','Oracle Amount','Variance','status']
#df4['status'] = np.where((df4['status'] == " ")&(df4['Variance'] == 0), 'MAtchiong',' ')

#df4.to_excel(output_file,"AIMS Data")

# create a excel writer object
with pd.ExcelWriter(output_file) as writer:
   
    # use to_excel function and specify the sheet_name and index
    # to store the dataframe in specified sheet
    df.to_excel(writer, sheet_name="AIMS Data", index=False)
    ora_df.to_excel(writer, sheet_name="Oracle Data", index=False)
    Reco.to_excel(writer, sheet_name="Reco", index=False)










            
        









  
    
    
    
    
    
