'''
Created on Jan 29, 2024

@author: carlo
'''
import re
import pandas as pd
import tabula
import itertools
from zoneinfo import _tzpath
from tabula import read_pdf


class Statement(object):
    
  
    columns=[]  
    area = [70, 30, 750, 570]
    table_page=2
    columns_to_drop=["col_3"]
    find_date=r'\A[0-9]{1,2}/[0-9]{1,2}'
    find_numbers=r'[0-9]*[0-9]+\.[0-9]*'
    raw_stmt=pd.DataFrame()
    new_stmt=pd.DataFrame()
    stm_as_string =""
    
    
    def __init__(self, date):
        self.date = date
    
    def open(self,file): 
        #Open raw pdf file on the specified area       
        self.raw_stmt=read_pdf(file, guess=False, lattice=False, stream=True, 
                       multiple_tables=False, area=self.area, pages=self.table_page)[0]
                       
       
    def parse(self):
        
        
        if len(self.raw_stmt.columns) < 3:
            return False
        
        idx=0;
        for col in self.raw_stmt.columns:                        
            self.columns.append("col_"+ str(idx))
            idx=idx+1
            
        self.raw_stmt.columns= self.columns          
        print(self.raw_stmt.columns)  
        
        for col in self.columns_to_drop:  
            self.new_stmt=self.raw_stmt.drop(col,axis=1)   
              
        #iterate over rows        
        for index,rows in self.new_stmt.iterrows(): 
            if isinstance(rows[self.columns[0]],str):  
            #look for row with date 
                if re.search(self.find_date,rows[self.columns[0]])==None:
                    #we drop raw without date information
                    self.new_stmt=self.new_stmt.drop(index=index)  
                else:
                    # Add year to the date
                    rows[self.columns[0]]=re.sub(r',','',rows[self.columns[0]])
                    rows[self.columns[0]]=re.sub(self.find_date,rf'\g<0>/{self.date},',rows[self.columns[0]])
                    self.new_stmt.loc[index]["col_0"]=rows[self.columns[0]]
                    for i in itertools.islice(self.columns,1,len(self.columns)-1) :                    
                        if isinstance(rows[i],str): 
                            #Remove coma from the numbers
                            rows[i] = re.sub(r',','',rows[i])
                            minus=""
                            #Numbers in the credit column should be negative
                            if i == "col_2":
                                minus="-"                        
                            self.new_stmt.loc[index][i] = re.sub(self.find_numbers
                                                        ,rf',{minus}$\g<0>',rows[i])
                    
                        
                                        
            else:
                self.new_stmt=self.new_stmt.drop(index=index)
                
        return True
            
            
    def get_string(self):
        if self.new_stmt.empty == False:
            temp_str=re.sub(r'\bcol.*',"",self.new_stmt.to_string(index=False)) 
            temp_str=re.sub(r'NaN',"",temp_str)
            for line in temp_str.split('\n'):
                self.stm_as_string += re.sub(r'^\s+',"",line)+'\n'
            return self.stm_as_string
        else:
            return ""       
            
        
    def clear(self):
        self.raw_stmt[0:0]
        self.new_stmt[0:0]  
        self.columns.clear()
        self.stm_as_string=''
    
  
  
    