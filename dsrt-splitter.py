from PyPDF2 import PdfFileWriter, PdfFileReader
import re, io, os
import fitz
from PIL import Image
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser

# PDF Splitter dengan rentang page
def split_pdf(file_origin, new_file, pg_start, pg_end):
    pdf_file = PdfFileReader(open(file_origin, "rb"))
    #np = pdf_file.getNumPages()
    pdf_new = PdfFileWriter()
    pgs = pg_start - 1
    pge = pg_end - 1
    for i in range(pgs, pg_end):
        #print("Split pdf halaman : %s"%(i+1))
        pdf_new.addPage(pdf_file.getPage(i))

    with open(new_file, 'wb') as out:
        print("Membuat PDF halaman %s-%s..."%(pg_start, pg_end))
        pdf_new.write(out)

    return pdf_new

def add_bs_loc_info(p, pg):
    with fitz.open(p) as pdf_doc:
        text = ''
        pg_spot = pdf_doc.loadPage(pg)
        pg_text = pg_spot.get_text()
        tx = pg_text.split("\n")
        nks_a = [tx[52], tx[51], tx[50], tx[49]]
        nks = ('').join(a for a in nks_a)
        elim = tx[11].replace('/', ' ')
        outp = [tx[10], elim, nks]
        return outp

def cek_info(p, pg):
    with fitz.open(p) as pdf_doc:
        text = ''
        pg_spot = pdf_doc.loadPage(pg-1)
        pg_text = pg_spot.get_text()
        tx = pg_text.split("\n")
        return tx


def pick_pdf(file_origin, new_file, pg):
    pdf_file = PdfFileReader(open(file_origin, "rb"))
    #np = pdf_file.getNumPages()
    pdf_new = PdfFileWriter()
    pdf_new.addPage(pdf_file.getPage(pg-1))

    with open(new_file, 'wb') as out:
        pdf_new.write(out)
    return pdf_new

# Convert PDF (with PyPDF2 and PDFMiner)
def convert_pdf(filename, convert_type):
    if convert_type == 'pdfminer':
        text = extract_text(filename, page_numbers=[0])
        return text
    else:
        pdf_file = PdfFileReader(open(filename, "rb"))
        np = pdf_file.getNumPages()
        for p in range(0, np):
            pg = pdf_file.getPage(p)
            tx = pg.extractText()
            print(tx)    

br = (228, 194, 8) #Logo Burung Garuda
# Get Page break list by image exists (Cocok untuk DSRT dan daftar berhalaman depan)
def getPagebreakList(file_name):
    page_breaks = []
    pdf_f = fitz.open(file_name)
    for i in range(len(pdf_f)):
        #print("Mengecek halaman %s"%(i))
        pg = pdf_f[i]
        img_list = pg.getImageList()
        for u in img_list:
            (u1, u2, u3, u4, u5, u6, u7, u8, u9) = u
            if (u3, u4, u5) == br: page_breaks.append(i) 
    return page_breaks

def split_pdf_by_page_break(pdf_name, filename_template, dirloc):
    inputpdf = PdfFileReader(open(pdf_name, "rb"))
    num_pages = inputpdf.numPages
    page_breaks = getPagebreakList(pdf_name)
    print(page_breaks)
    if dirloc == ".":
        for n in range(0, len(page_breaks)):
            if n != len(page_breaks)-1: split_pdf(pdf_name, "%s_%s.pdf"%(filename_template, n+1), page_breaks[n]+1, page_breaks[n+1])
            else: split_pdf(pdf_name, "%s_%s.pdf"%(filename_template, n+1), page_breaks[n]+1, num_pages)
    else:
        if not os.path.exists(dirloc):
            os.makedirs(dirloc)
            print("Folder sudah dibuat.")
            for n in range(0, len(page_breaks)):
                bs = add_bs_loc_info(pdf_name, page_breaks[n])
                #if n != len(page_breaks)-1: split_pdf(pdf_name, "%s\\%s_%s_%s.pdf"%(dirloc, filename_template, n+1), page_breaks[n]+1, page_breaks[n+1])
                if n != len(page_breaks)-1: split_pdf(pdf_name, "%s\\%s_%s_%s_%s.pdf"%(dirloc, filename_template, bs[0], bs[1], bs[2]), page_breaks[n]+1, page_breaks[n+1])
                #else: split_pdf(pdf_name, "%s\\%s_%s.pdf"%(dirloc, filename_template, n+1), page_breaks[n]+1, num_pages)
                else: split_pdf(pdf_name, "%s\\%s_%s_%s_%s.pdf"%(dirloc, filename_template, bs[0], bs[1], bs[2]), page_breaks[n]+1, num_pages)
                print("File %s_%s_%s dibuat."%(bs[0], bs[1], bs[2]))
    print("Dokumen PDF berhasil dipecah sebanyak %d dokumen."%(len(page_breaks)))


#pdf_name = "lf_sp2020_p_6401_20220412.pdf"
pdf_name = "F:\_KANTOR 2021\SPLF 2021\PRELIST\lf_sp2020_p_64_20220419_Tahap2\lf_sp2020_p_6404_20220419.pdf"
pdf_splitted = "splf"
pdf_outp = "mypdf.pdf"

split_pdf_by_page_break(pdf_name, pdf_splitted, "D:\\SPLIT_PRELIST_KUTIM_6")
#print(getPagebreakList("F:\\_KANTOR 2021\\SPLF 2021\\PRELIST\\lf_sp2020_p_6404_20220412.pdf"))
#split_pdf(pdf_name, "lf_split_kutim.pdf", 1, 5792)
#split_pdf(pdf_name, "lf_split_kutim_3.pdf", 8740, 13370)
#split_pdf(pdf_name, "lf_split_kutim_4.pdf", 13371, 16098)
#split_pdf(pdf_name, "lf_split_kutim_5.pdf", 16099, 20500)