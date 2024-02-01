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
import fitz


class Statement(object):
    
  
    columns=[]         
    init_table_mark_position=[]
    end_table_mark_position=[]
    columns_to_drop=["col_4"]
    find_date=r'\A[0-9]{1,2}/[0-9]{1,2}'
    find_numbers=r'[0-9]*[0-9]+\.[0-9]*'
    raw_stmt=pd.DataFrame()
    new_stmt=pd.DataFrame()
    stm_as_string =""
    init_table_mark = "Transaction history"
    end_table_mark ="Totals"
    
    
    def __init__(self, date):
        self.date = date
        
    
    def open(self,file): 
        
        pdf_document = fitz.open(file)
        
        #look for first marker on pages, if the table is bigger than one page two or more
        #markers will be find         
        for page in pdf_document:
            text_instances = page.search_for(self.init_table_mark)        
            for text_instance in text_instances:
                self.init_table_mark_position.append({"page":page.number,
                                                      "x0":int(text_instance.x0),
                                                      "y0":int(text_instance.y0),
                                                      "x1":int(page.mediabox_size.x),
                                                      "y1":int(page.mediabox_size.y)
                                                      })
                
        #look for the unique end marker (hopefully)                                                    
        for page in pdf_document:
            text_instances = page.search_for(self.end_table_mark)
            for text_instance in text_instances:
                self.end_table_mark_position.append({"page":page.number,"x0":int(text_instance.x0),"y0":int(text_instance.y0)})
                
        self.init_table_mark_position[-1]["y1"] = self.end_table_mark_position[0]["y0"]    
                                        
        #Open raw pdf file on the specified area
        for table in self.init_table_mark_position:       
            self.raw_stmt=read_pdf(file, guess=False, lattice=False, stream=True,multiple_tables=False,
                                   area = [table["y0"], table["x0"], table["y1"], table["x1"]], pages = table["page"]+1)[0]
            print(self.raw_stmt)
                       
        #print(self.raw_stmt.to_string())
                       
       
    def parse(self):
        
        
        if len(self.raw_stmt.columns) < 3:
            return False
        
        idx=0;
        #Change name to columns
        for col in self.raw_stmt.columns:                        
            self.columns.append("col_"+ str(idx))
            idx=idx+1
            
        self.raw_stmt.columns= self.columns          
        #print(self.raw_stmt.columns)  
        
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
                    rows[self.columns[1]]=re.sub(r',','',rows[self.columns[1]])
                    rows[self.columns[1]]=re.sub(r'\A\s*','',rows[self.columns[1]])
                    #rows[self.columns[1]].lstrip()
                    rows[self.columns[0]]=re.sub(self.find_date,rf'\g<0>/{self.date},',rows[self.columns[0]])
                    self.new_stmt.loc[index]["col_0"]=rows[self.columns[0]]
                    self.new_stmt.loc[index]["col_1"]=rows[self.columns[1]]
                    for i in itertools.islice(self.columns,2,len(self.columns)-1) :                    
                        if isinstance(rows[i],str): 
                            #Remove coma from the numbers
                            rows[i] = re.sub(r',','',rows[i])
                            minus="-"
                            #Numbers in the credit column should be negative
                            if i == "col_2":
                                minus=""                        
                            self.new_stmt.loc[index][i] = re.sub(self.find_numbers
                                                        ,rf',{minus}$\g<0>',rows[i])
                    
                        
                                        
            else:
                self.new_stmt=self.new_stmt.drop(index=index)
                
        return True
            
            
    def get_string(self):
        if self.new_stmt.empty == False:
            temp_str=re.sub(r'\bcol.*\n',"",self.new_stmt.to_string(index=False)) 
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
    
  
  
    