import pdfplumber, sys, os, utils
from PyQt6 import QtWidgets, uic, QtCore
from mainwindown import Ui_MainWindow
from PyQt6.QtCore import QFile
from PyQt6.QtWidgets import QFileDialog


class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
            super().__init__(*args,**kwargs)
            self.setupUi(self)
            self.amount_text.setText('0.0')
            
    @QtCore.pyqtSlot()        
    def on_Open_button_clicked(self):
        self.fname=QFileDialog.getOpenFileName(self, 'Openfile', './', '*.pdf', None)
        self.pdf_browser.clear()
        self.pdf = pdfplumber.open(self.fname[0])
        self.search_button.setEnabled(True)
        self.search_text.setEnabled(True)
        for page in self.pdf.pages :                                    
            self.pdf_browser.append(page.extract_text())
        
    @QtCore.pyqtSlot()         
    def on_search_button_pressed(self):
        if self.search_text.text() != "":
            self.total = 0
            self.text = self.search_text.text()            
            self.search_in_pdf(self.search_text.text(), self.pdf_browser.toPlainText()) 
            str_float = "{:.2f}".format(self.total)           
            self.amount_text.setText(str_float)
        
                
    def search_in_pdf(self, text_to_find, page_text):
        for row in page_text.split('\n'):
            if row.find(text_to_find) != -1:                        
                amount=(row.split()[-1])
                amount = amount.replace(',','')
                if amount.find('CR') != -1 :                
                    amount = amount.replace('CR','')
                    self.total -= float(amount)
                else :
                    self.total += float(amount)    
                
"""  
    def main(self):                
        self.open_pdf()
        for text in self.text_to_search :    
            for page in self.pdf.pages :        
                self.search_in_pdf(text, page.extract_text())
            print (text + " = " + str(self.total))
            self.total = 0.0
"""


    
if __name__ == '__main__': 
    
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
    
        