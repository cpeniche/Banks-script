'''
Created on Feb 2, 2024

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
    
  columns = []         
  init_table_mark_position = []
  end_table_mark_position = []
  columns_to_drop = [1,3,4,6]
  find_date = r'\A[0-9]{1,2}/[0-9]{1,2}'
  find_numbers = r'[0-9]*[0-9]+\.[0-9]*'
  raw_table_list = []
  new_table_list = []
  stm_as_string = ""
  init_table_mark = "Reference"
  end_table_mark = "Total Interest charged for this period"


  def __init__(self, date):
    self.date = date
  
  
  def open(self, file): 
      
    pdf_document = fitz.open(file)
    
    # look for first marker on pages, if the table is bigger than one page two or more
    # markers will be find         
    for page in pdf_document:
      text_instances = page.search_for(self.init_table_mark)        
      for text_instance in text_instances:
          self.init_table_mark_position.append({"page":page.number,
                                                "x0":0,#int(text_instance.x0),
                                                "y0":int(text_instance.y0),
                                                "x1":int(page.mediabox_size.x),
                                                "y1":int(page.mediabox_size.y)
                                                })
          
    # look for the unique end marker (hopefully)                                                    
    for page in pdf_document:
      text_instances = page.search_for(self.end_table_mark)
      for text_instance in text_instances:
        self.end_table_mark_position.append({"page":page.number,
                                               "x0":int(text_instance.x0),
                                               "y0":int(text_instance.y0)})
            
    self.init_table_mark_position[-1]["y1"] = self.end_table_mark_position[0]["y0"]    
                                    
    # Open raw pdf file on the specified area
    for idx, table in enumerate(self.init_table_mark_position): 
      self.raw_table_list.append({"index":idx, "table": read_pdf(file,
                            guess=False,
                            lattice=False,
                            stream=True,
                            multiple_tables=False,
                            area=[table["y0"], table["x0"], table["y1"], table["x1"]],
                            pages=table["page"] + 1)[0]})
        
    #===========================================================================
    # for table in self.raw_table_list: 
    #   print(table["table"].to_string())
    #===========================================================================
      
      
  def parse(self):
      
    new_table = []
      
    for tbl_idx, table in enumerate(self.raw_table_list): 
      if len(table["table"].columns) < 3:
        return False
      
      #print(table["table"].columns)  
            
      temp = table["table"]
      # drop undesired columns    
      temp.drop(temp.columns[self.columns_to_drop], axis=1, inplace=True)         
      new_table.append(temp)   
      
      # Change name to columns
      for idx, col in enumerate(new_table[tbl_idx].columns): 
        self.columns.append("col_" + str(idx))
                    
      new_table[tbl_idx].columns = self.columns          
            
      #print(new_table[tbl_idx].columns)   
            
      # iterate over rows        
      for index, rows in new_table[tbl_idx].iterrows(): 
        if isinstance(rows[self.columns[0]], str): 
        # look for row with date 
            if re.search(self.find_date, rows[self.columns[0]]) == None:
                # we drop row without date information
                new_table[tbl_idx] = new_table[tbl_idx].drop(index=index)  
            else:
                # Add year to the date
                rows[self.columns[1]] = re.sub(r',', '', rows[self.columns[1]])
                rows[self.columns[1]] = re.sub(r'\A\s*', '', rows[self.columns[1]])
                
                rows[self.columns[0]] = re.sub(self.find_date, rf'\g<0>/{self.date},', rows[self.columns[0]])
                new_table[tbl_idx].loc[index]["col_0"] = rows[self.columns[0]]
                new_table[tbl_idx].loc[index]["col_1"] = rows[self.columns[1]]
                
                # Remove coma from the numbers                
                if isinstance(rows[self.columns[2]], str):
                  if re.search(r"\A0.00", rows[self.columns[2]]) == None:
                    rows[self.columns[2]] = re.sub(r',', '', rows[self.columns[2]])                                                                                  
                    new_table[tbl_idx].loc[index][self.columns[2]] = re.sub(self.find_numbers
                                                      ,r',$\g<0>', rows[self.columns[2]])
                  else:
                    #drop rows with zero values in the amount
                    new_table[tbl_idx] = new_table[tbl_idx].drop(index=index)
                                    
        else:
          new_table[tbl_idx] = new_table[tbl_idx].drop(index=index)
        
      self.new_table_list.append(new_table[tbl_idx])
      self.columns.clear()
            
    return True
          
  def get_string(self):
    
    for table in self.new_table_list:
      if table.empty == False:
        temp_str = re.sub(r'\bcol.*\n', "", table.to_string(index=False)) 
        temp_str = re.sub(r'NaN', "", temp_str)
        for line in temp_str.split('\n'):
          self.stm_as_string += re.sub(r'^\s+', "", line) + '\n'                
      else:
        return ""      
    return self.stm_as_string 
      
  def clear(self):
    self.raw_table_list.clear()
    self.new_table_list.clear()    
    self.columns.clear()
    self.stm_as_string = ''
    self.init_table_mark_position.clear()
    self.end_table_mark_position.clear()