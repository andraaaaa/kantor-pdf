from PyPDF2 import PdfFileWriter, PdfFileReader
import re, io, os
import fitz
from PIL import Image
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser

# VARIABEL INI DIGUNAKAN SEBAGAI PEMBENTUK PAGE BREAK ANTAR FILE.
# Bisa diganti tergantung kebutuhan dan gambar target
# Untuk menggunakan silakan cek pada fungsi get_pics()

br = (100, 100, 8) #Logo Burung Garuda

# ---------------------------------------------------------------------
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

def add_bs_loc_info_v1(p, pg):
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
# ------------------------------------------
# UNTUK DSRT
# Untuk PPLF, index array sudah disesuaikan. Silakan diganti indexnya dengan
# menggunakan fungsi cek_info()

def add_bs_dsrt(p, pg):
    a = cek_info(p, pg)
    outp = [clean_text(a[11]), clean_text(a[14]), clean_text(a[21])]
    return outp

# Untuk nama wilayah yang menggunakan garis miring, diganti strip menghindari kesalahan rename file
def clean_text(t):
    t = t.replace('/', '-')
    t = re.sub(' +', ' ', t)
    return t

# Untuk memetakan array dari teks PDF. Berguna untuk mengambil elemen nama file yang akan dibuat
def cek_info(p, pg):
    with fitz.open(p) as pdf_doc:
        text = ''
        pg_spot = pdf_doc.loadPage(pg-1)
        pg_text = pg_spot.get_text()
        tx = pg_text.split("\n")
        return tx

# Ambil satu halaman PDF
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

# Ambil pratinjau gambar dari PDF halaman tertentu. 
def get_pics(p, pg):
    filepdf = fitz.open(p)
    page = filepdf[pg-1]
    image_list = page.getImageList()
    # printing number of images found in this page
    if image_list:
        print(f"[+] Found a total of {len(image_list)} images in page {pg}")
        print(image_list)
    else:
        print("[!] No images found on page", pg)
    for image_index, img in enumerate(page.getImageList(), start=1):
        # get the XREF of the image
        xref = img[0]
        # extract the image bytes
        base_image = filepdf.extractImage(xref)
        image_bytes = base_image["image"]
        # get the image extension
        image_ext = base_image["ext"]
        # load it to PIL
        image = Image.open(io.BytesIO(image_bytes))
        # save it to local disk
        image.save(open(f"image{pg}_{image_index}.{image_ext}", "wb"))

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


# [MAIN LINE] (Updated 5/29 9:37 PM) Membuat daftar dari page break yang sudah ada
def build_daftar(pdf_name, filename_template, dirloc):
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
                bs = add_bs_dsrt(pdf_name, page_breaks[n]+1)
                #if n != len(page_breaks)-1: split_pdf(pdf_name, "%s\\%s_%s_%s.pdf"%(dirloc, filename_template, n+1), page_breaks[n]+1, page_breaks[n+1])
                if n != len(page_breaks)-1: split_pdf(pdf_name, "%s\\%s_%s_%s_%s.pdf"%(dirloc, filename_template, bs[0], bs[1], bs[2]), page_breaks[n]+1, page_breaks[n+1])
                #else: split_pdf(pdf_name, "%s\\%s_%s.pdf"%(dirloc, filename_template, n+1), page_breaks[n]+1, num_pages)
                else: split_pdf(pdf_name, "%s\\%s_%s_%s_%s.pdf"%(dirloc, filename_template, bs[0], bs[1], bs[2]), page_breaks[n]+1, num_pages)
                print("File (%d/%d) %s_%s_%s dibuat."%(n+1, len(page_breaks), bs[0], bs[1], bs[2]))
    print("Dokumen PDF berhasil dipecah sebanyak %d dokumen."%(len(page_breaks)))


ct = "D:\\LFP2022.pdf"

#  CONTOH PENGGUNAAN
build_daftar(ct, "dsrt", "D:\\splitted")
