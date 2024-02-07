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
  find_date = {'numbers':r'\A[0-9]{1,2}/[0-9]{1,2}',
               'letters':r'\A'
               }
  stm_as_string = ""

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
      
    
    pdf_document = fitz.open(file)
    
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
      self.raw_table_list.append({"index":idx, "table": read_pdf(file,
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
           
      # drop undesired columns    
      temp.drop(columns=commands["Drop"],inplace=True)        
      new_table.append(temp)   
      
      # Change name to columns
      if 'Rename' in commands.keys():
        if len(commands['Rename']) == len(new_table[tbl_idx].columns):
          new_table[tbl_idx].columns = commands['Rename']  
        else:
          return False;
                                                
      new_table[tbl_idx] = self.drop_unused_rows(new_table[tbl_idx],commands) 
      new_table[tbl_idx] = self.remove_comas(new_table[tbl_idx])  
      
      print(new_table[tbl_idx])   
      self.new_table_list.append(new_table[tbl_idx])
                
    return True
  
  def drop_unused_rows(self,table,commands): 
    regex = self.find_date[commands["Date Format"][0]]   
    for index, rows in table.iterrows():
      if isinstance(rows["Date"], str) == True:
        if re.search(regex, rows["Date"]) == None:                            
        # we drop rows without date information
          table = table.drop(index=index)
        else:
        #Add year and comma
          table.loc[index,"Date"]=re.sub(regex,rf'\g<0>/{self.date}',rows["Date"])
      else:
          table = table.drop(index=index)  
    return table 
  
  def remove_comas(self, table):
    for index , rows in table.iterrows():
      for col in itertools.islice(table.columns, 1, len(table.columns)):
        if isinstance(rows[col], str) == True:
          table.loc[index,col]=re.sub(r',',r'', rows[col])
          table.loc[index,col]=re.sub(r'\A.*',r',\g<0>', rows[col]) 
        else:
          table.loc[index,col]=",0.00" 
    return table      
          
  def get_string(self, add_header):
    
    for table in self.new_table_list:
      if table.empty == False:
        if add_header:
          temp_str = re.sub(r'\w+\s*', r'\g<0>,', table.to_string(index=False), len(table.columns)-1)
        else:
          temp_str = re.sub(r'\A.*\n',"", table.to_string(index=False), 1)              
        for line in temp_str.split('\n'):
          self.stm_as_string += re.sub(r'^\s+', "", line) + '\n'                
      else:
        return ""      
    return self.stm_as_string 
      
  def clear(self):
    self.raw_table_list.clear()
    self.new_table_list.clear()    
    self.header_coordinates.clear()
    self.stm_as_string = ''
    self.end_marker_coordinates.clear()
    
    