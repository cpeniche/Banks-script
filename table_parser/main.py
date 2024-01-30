import fitz
import sys
 
#reads table from pdf file

pdf_document = fitz.open(sys.argv[1])


# Specify the text you want to search for

search_text = 'Date'


# Iterate through each page in the PDF

for page in pdf_document:


    # Use the `search_for` method to find instances of the search text on the page

    text_instances = page.search_for(search_text)


    # Iterate through each instance and print the bounding box coordinates

    for text_instance in text_instances:

        x0, y0, x1, y1 = text_instance.bbox

        print(f"Page {page_num + 1}:")

        print(f"Text: {search_text}")

        print(f"Bounding Box: ({x0}, {y0}) - ({x1}, {y1})") 