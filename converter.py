import tabula

target_file = "F:\\_KANTOR 2021\\SPLF 2021\\Pra Pemutakhiran\\LF.SP2020_dsbs.pp_64\\lf.sp2020_dsbs.pp_6401.pdf"
df = tabula.read_pdf(target_file, pages="all")

tabula.convert_into(target_file, "dsbs.csv", output_format="csv", pages='all')
print(df)