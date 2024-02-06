'''
Created on Feb 6, 2024

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
  
  header_coordinates = []
  end_marker_coordinates=[]
  raw_table_list = []
  new_table_list = []

  def __init__(self, date):
    self.date = date
    
    
  def search_for_header(self, header, block, page, coordinates):    
    for column_name in header:
      if re.search(column_name,block[4]) == None:
        return False            
    coordinates.append({"page":page.number,
                                    "x0":int(block[0]),
                                    "y0":int(block[1]),
                                    "x1":int(page.mediabox_size.x),
                                    "y1":int(page.mediabox_size.y)

                                    })
    return True;
    
    
  
  def open(self, file, commands): 
      
    
    pdf_document = fitz.open(file[0])
    
    # look for first marker on pages, if the table is bigger than one page two or more
    # markers will be find         
    for page in pdf_document:     
      blocklist = page.get_text("blocks", sort=True)
      for block in blocklist:
        self.search_for_header(commands["Table Header"],block,page,self.header_coordinates)
        self.search_for_header(commands["Table End"],block,page,self.end_marker_coordinates)                           
        
                                                                  
    self.header_coordinates[-1]["y1"] = self.end_marker_coordinates[0]["y0"]    
                                    
    # Open raw pdf file on the specified area
    for idx, table in enumerate(self.header_coordinates):       
      self.raw_table_list.append({"index":idx, "table": read_pdf(file[0],
                      guess=False,
                      lattice=False,
                      stream=True,
                      multiple_tables=False,
                      area=[table["y0"], table["x0"], table["y1"], table["x1"]],
                      pages=table["page"] + 1)[0]})
        
    for table in self.raw_table_list: 
      print(table["table"])
                         
  def parse(self,commands):
      
    new_table = []
      
    for tbl_idx, table in enumerate(self.raw_table_list): 
      if len(table["table"].columns) != len(commands["Table Header"]):
        return False
      else:
        table["table"].columns = commands['Table Header']
            
      temp = table["table"]
      print(temp.columns)
      
      # drop undesired columns    
      temp.drop(columns=commands["Drop"],inplace=True)
      print(temp.columns)         
      new_table.append(temp)   
      
      # Change name to columns
      if 'Rename' in commands.keys():
        if len(commands['Rename']) == len(new_table[tbl_idx].columns):
          new_table[tbl_idx].columns = commands['Rename']  
        else:
          return False;
                                          
      print(new_table[tbl_idx].columns)    
            
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
    