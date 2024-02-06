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
                      default = "./")
  parser.add_argument('-c','--config',required=True, help='Command specification for document parse')
  parser.add_argument('-y','--year', required=True, help="statements year")
  
  return parser.parse_args()

def main():
  
  file_list=[]
  
  parser = argparse.ArgumentParser(description='Extract Banks Statments transaction details')
  args=create_arguments(parser)
   
  #Read all files in the directory
  if args.filename == '*':  
    file_list = Path(args.directory).rglob('*.pdf')
  else:
    for file in args.filename:      
      file_list.append(args.directory+ '/' + file[0])
  
  
  #Read config file
  config_file=open(args.config)
  commands = json.loads(config_file.read())
        
  file_data = ""
             
  for file in file_list:
    print("-----------" + str(file) + "---------------") 
    
    Stmt = Bank.Statement(args.year)
    Stmt.open(file_list,commands)    
    if Stmt.parse(commands) == True:
      file_data += Stmt.get_string()
    else:
      file_data += "\n**************** Error at file : " + str(file) + "*****************\n"
    # print(file_data)
    Stmt.clear()
  #=============================================================================
  # ofile = open(sys.argv[1] + "/" + str(year) + '_transactions.csv', 'w')  
  # ofile.write(file_data) 
  # ofile.close()   
  # else:
  #   if sys.argv[3] == WF:
  #     Stmt = WF.Statement(year)
  #   else:
  #     Stmt = Bofa.Statement(year) 
  #   Stmt.open(file)
  #   Stmt.parse()        
  #   file_data = Stmt.get_string()
  #   ofile = open(sys.argv[1] + '.csv', 'w')  
  #   ofile.write(file_data) 
  #   ofile.close() 
  #=============================================================================
        
    print("Parser done")
    

if __name__ == '__main__':
  main()
