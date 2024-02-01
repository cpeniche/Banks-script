'''
Created on Jan 29, 2024

@author: carlo
'''
from pathlib import Path
import WellsFargo as WF
import sys

if __name__ == '__main__':
    
    file_data = ""
    year = sys.argv[2]
    file = sys.argv[1]
    if len(sys.argv) == 4:
      if sys.argv[3] == '-batch':            
        pathlist = Path(sys.argv[1]).rglob('*.pdf')                   
        for file in pathlist :
          print("-----------" + str(file) + "---------------")     
          Stmt = WF.Statement(year)
          Stmt.open(str(file))
          if Stmt.parse() == True:
            file_data += Stmt.get_string()
          else:
            file_data += "\n**************** Error at file : "+ str(file) +"*****************\n"
          #print(file_data)
          Stmt.clear()
        ofile = open(sys.argv[1]+"/"+str(year)+'_transactions.csv','w')  
        ofile.write(file_data) 
        ofile.close()   
    else :
      Stmt = WF.Statement(year)
      Stmt.open(file)
      Stmt.parse()        
      file_data=Stmt.get_string()
      ofile = open(sys.argv[1] +'.csv','w')  
      ofile.write(file_data) 
      ofile.close()  
    
    print("Parser done")   
    
    
    
    
    
    
    