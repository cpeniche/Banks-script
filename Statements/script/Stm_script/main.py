import re
import sys
from telnetlib import theNULL


months =[["Jan ","01"],
         ["Feb ","02"],
         ["Dec ","12"]]


with open(sys.argv[1],'r') as stm:
    new_stm = stm.read()
    
    #Look for lines    
    print(re.sub(r"(?P<line>\bDec.\b)","\g<line>", new_stm, flags=re.M))
    
    
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