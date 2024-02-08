'''
Created on Jan 29, 2024

@author: carlo
'''
from pathlib import Path
import argparse
import Statement as Bank
import json
import sys


    
def create_arguments(parser):    
  
  parser.add_argument('-f','--filename', required=True, help='file name or * for all file in the directory',
                      nargs='+', action='append')
  parser.add_argument('-d','--directory', required=False, help='Directory path of pdf files',
                      default = ".")
  parser.add_argument('-c','--config',required=True, help='Command specification for document parse')
  parser.add_argument('-y','--year', required=True, help="statements year")
  parser.add_argument('-o','--output',default="output.cvs", help="Output file name")
  
  return parser.parse_args()

def main():
  
  file_list=[]
  
  parser = argparse.ArgumentParser(description='Extract Banks Statments transaction details')
  args=create_arguments(parser)
   
  #Read all files in the directory
  if args.filename[0][0] == "all":  
    gen_file_list = sorted(Path(args.directory).rglob('*.pdf'))
    for file in gen_file_list:
      file_list.append(str(file))
    
    print(type(file_list))
  else:
    for file in args.filename:      
      file_list.append(args.directory+ '/' + file[0])      
  
  
  #Read config file
  config_file=open(args.config)
  commands = json.loads(config_file.read())
        
  file_data = ""
  Stmt = Bank.Statement(args.year)           
  for file in file_list:
    print("-----------" + str(file) + "---------------") 

    Stmt.open(str(file),commands)    
    if Stmt.parse(commands) == True:
      file_data += Stmt.get_string(file_data=="")
    else:
      file_data += "\n**************** Error at file : " + str(file) + "*****************\n"   
    Stmt.clear()      
  file=open(args.directory+'/'+args.output,'w')
  file.write(file_data)
  file.close()
  
  
  print("****** Parser done **********")
    

if __name__ == '__main__':
  main()
