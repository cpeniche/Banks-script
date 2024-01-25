import re
import sys
from telnetlib import theNULL


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

#===============================================================================
# month_pattern = '|'.join(months)
# print(month_pattern)    
#===============================================================================


with open(sys.argv[1],'r') as stm:
    file_lines = stm.readlines()
     
    for lines in file_lines:
        #Process line by line to look for dates 
        data = re.search(rf"(?P<line>\b({'|'.join(months)}).*\b)", lines, flags=re.M)
        if data != None:                    
            if (date := re.search(r'[^\s]+',data.group(0))) != None:                         
                new_stm += re.sub(r'[^\s]+',months[date.group(0)] ,data.group(0), count=1)  + '\n'                
    
    
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

print (new_stm)
 
 
 