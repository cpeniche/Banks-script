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
    
  columns = []         
  init_table_mark_position = []
  end_table_mark_position = []
  columns_to_drop = ["col_4"]
  find_date = r'\A[0-9]{1,2}/[0-9]{1,2}'
  find_numbers = r'[0-9]*[0-9]+\.[0-9]*'
  raw_table_list = []
  new_table_list = []
  stm_as_string = ""
  init_table_mark = "Transaction history"
  end_table_mark = "Totals"
  
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
                                                "x0":int(text_instance.x0),
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
        
    # for table in self.raw_table_list: 
    #   print(table["table"])
                         
  def parse(self):
      
    new_table = []
      
    for tbl_idx, table in enumerate(self.raw_table_list): 
      if len(table["table"].columns) < 3:
        return False
            
      # Change name to columns
      for idx, col in enumerate(table["table"].columns): 
        self.columns.append("col_" + str(idx))
                    
      table["table"].columns = self.columns          
      # print(self.table.columns)  
      
      for col in self.columns_to_drop: 
        new_table.append(table["table"].drop(col, axis=1))   
            
      # iterate over rows        
      for index, rows in new_table[tbl_idx].iterrows(): 
        if isinstance(rows[self.columns[0]], str): 
        # look for row with date 
            if re.search(self.find_date, rows[self.columns[0]]) == None:
                # we drop raw without date information
                new_table[tbl_idx] = new_table[tbl_idx].drop(index=index)  
            else:
                # Add year to the date
                rows[self.columns[1]] = re.sub(r',', '', rows[self.columns[1]])
                rows[self.columns[1]] = re.sub(r'\A\s*', '', rows[self.columns[1]])
                
                rows[self.columns[0]] = re.sub(self.find_date, rf'\g<0>/{self.date},', rows[self.columns[0]])
                new_table[tbl_idx].loc[index]["col_0"] = rows[self.columns[0]]
                new_table[tbl_idx].loc[index]["col_1"] = rows[self.columns[1]]
                for i in itertools.islice(self.columns, 2, len(self.columns) - 1): 
                    if isinstance(rows[i], str): 
                        # Remove coma from the numbers
                        rows[i] = re.sub(r',', '', rows[i])
                        minus = "-"
                        # Numbers in the credit column should be negative
                        if i == "col_2":
                            minus = ""                        
                        new_table[tbl_idx].loc[index][i] = re.sub(self.find_numbers
                                                    , rf',{minus}$\g<0>', rows[i])
                                    
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
    
