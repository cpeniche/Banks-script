import re
import sys
from telnetlib import theNULL

import tabula
from tabula import read_pdf
from tabulate import tabulate
import pandas
 
#reads table from pdf file

months ={"Jan":"01",
         "Feb":"02",
         "Mar":"03",
         "Apr":"04",
         "May":"05",
         "Jun":"06",
         "Jul":"07",
         "Aug":"08",
         "Sep":"09",
         "Oct":"10",
         "Nov":"11",
         "Dec":"12",
        }

new_stm=""
area = [70, 30, 750, 570]

df_list = read_pdf(sys.argv[1], guess=False, lattice=False, stream=True, 
              multiple_tables=False, area=area, pages="2") 


stmt = df_list[0]

stmt=stmt.drop(columns='Unnamed: 3').to_string()
#print(stmt)
for line in stmt.split('\n'):    
    if data:=re.search(r'\b[0-9]+\s+[0-9]{1,2}/[0-9]{1,2}.*',line):        
        new_stm += data.group(0) + '\n'
ss=""
for line in new_stm.split('\n'): 
    ss += re.sub(r'\A[0-9]+\s+','',line) + '\n'
    
ss= re.sub(r'NaN',r'',ss)

print(ss)
#===============================================================================
# ofile = open('output.txt','w')
# 
# orig_stdout = sys.stdout
# sys.stdout = ofile
# print(df)
# sys.stdout = orig_stdout
# ofile.close()
#===============================================================================

month_pattern = '|'.join(months)

#===============================================================================
# with open(df,'r') as stm:
#     file_lines = stm.readlines()
#       
#     for lines in file_lines:
#         #Process line by line to look for dates 
#         #data = re.search(rf"(?P<line>\b({'|'.join(months)}).*\b)", lines, flags=re.M)
#         data = re.search(r"(?P<line>\A[0-9]+/.*\b)", lines, flags=re.M)
#         if data != None:      
#             new_stm = new_stm + data.group(0) + '\n'              
#             #===================================================================
#             # if (date := re.search(r'(?P<date>[^\s]+',data.group(0))) != None:                         
#             #     new_stm += re.sub(r'[^\s]+',months[date.group(0)] ,data.group(0), count=1)  + '\n'                
#             #===================================================================
#     #Add year
#     new_stm = re.sub(r'(?P<date>[0-9]{,2}/[0-9]{,2}[^\s]+)','\g<date>/2022,',new_stm,flags=re.M)
#===============================================================================
    
#===============================================================================
#     for i in range(len(months)):        
#         date = re.compile(months[i][0])    
#         new_stm = date.sub(months[i][1]+"/",new_stm)
#     
# #   Create date pattern group
#     date= re.compile("(?P<date>[0-9][0-9]/[0-9][0-9])")
#     new_stm = date.sub("\g<date>/2020, $",new_stm)
#     
#     sign = re.compile(r"\$ -")   
#     new_stm = sign.sub(r"-$",new_stm)
#     
#     space = re.compile(r"\$ ")
#     new_stm = space.sub(r"$",new_stm)
#     
#     space = re.compile(r"(?P<digit>[0-9] )")
#     new_stm = space.sub(r"\g<digit>,",new_stm)
#     
#===============================================================================

#print (new_stm)
 
 
 