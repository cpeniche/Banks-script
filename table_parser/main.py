import re
import sys
from telnetlib import theNULL

import tabula
from tabula import read_pdf
from tabulate import tabulate
import pandas
from builtins import isinstance
from pathlib import Path
 
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


directory = sys.argv[1]
new_stm=""
area = [70, 30, 750, 570]
pathlist = Path(sys.argv[1]).rglob('*.pdf')

for path in pathlist:
    df_list = read_pdf(str(path), guess=False, lattice=False, stream=True, 
                  multiple_tables=False, area=area, pages="2") 
    
    
    
    stmt = df_list[0]
    print(str(path)+'\n')
    print(stmt)
    print('**************************')
    stmt.reset_index()
    minus=""
    
    #Remove unused column.
    stmt=stmt.drop(stmt.columns[[3]],axis=1)
     
    for index,rows in stmt.iterrows():
        if isinstance(rows[0],str):  
            #look for row with date 
            if re.search(r'\A[0-9]{1,2}/[0-9]{1,2}',rows[0])==None:
                stmt=stmt.drop(index=index)  
            else:
                # Add year to the date
                stmt.loc[index][0]=re.sub(r'(?P<dates>\A[0-9]{1,2}/[0-9]{1,2})','\g<dates>/2019,',rows[0])
                for i in range(1,3):
                    if isinstance(rows[i],str): 
                        #Remove coma from the numbers
                        rows[i] = re.sub(r',','',rows[i])
                        minus=""
                        #Numbers in the second column should be negative
                        if i == 2:
                            minus="-"                        
                        stmt.loc[index][i] = re.sub(r'(?P<numbers>[0-9]*[0-9]+\.[0-9]*)'
                                                    ,rf',{minus}$\g<numbers>',rows[i])
                    
                    
                                        
        else:
            stmt=stmt.drop(index=index)
    
    file_data=""
    
    output=re.sub(r'\bUnnamed.*',"",stmt.to_string(index=False)) 
    output=re.sub(r'NaN',"",output)
    for line in output.split('\n'):
        file_data += re.sub(r'^\s+',"",line) +'\n' 
   
    ofile = open(str(path)+'.csv','w')  
    ofile.write(file_data) 
    ofile.close()    
             
   
#===============================================================================
#     if data:=re.search(r'\b[0-9]+\s+[0-9]{1,2}/[0-9]{1,2}.*',line):        
#         new_stm += data.group(0) + '\n'
#     else
#         stmt.drop(index=)
# ss=""
# for line in new_stm.split('\n'): 
#     ss += re.sub(r'\A[0-9]+\s+','',line) + '\n'
#     
# ss= re.sub(r'NaN',r'',ss)
#===============================================================================

#print(ss)
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
 
 
 