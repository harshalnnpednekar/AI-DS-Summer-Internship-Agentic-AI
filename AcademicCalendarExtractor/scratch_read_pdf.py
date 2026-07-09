import fitz
import sys

pdf_path = r'v:\summer internship\academic calendar 2.pdf'
try:
    doc = fitz.open(pdf_path)
    num_pages = doc.page_count
    print(f'Number of pages: {num_pages}')
    
    if num_pages > 0:
        first_page = doc.load_page(0)
        text = first_page.get_text()
        print('--- Text from First Page ---')
        print(text)
        print('----------------------------')
        if text.strip():
            print('Readable: Yes')
        else:
            print('Readable: No (Might be scanned/images)')
    else:
        print('Readable: No (Empty PDF)')
        
    doc.close()
except Exception as e:
    print(f'Error reading PDF: {e}')
