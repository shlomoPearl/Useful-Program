import PyPDF2

nis = "\u20AA"


def parse_bill(pageObj, ):
    electric = 0
    water = 0
    # extracting text from page
    bill_list = pageObj.extract_text().splitlines()
    for line in bill_list:
        if 'חשמל' in line.split(' '):
            electric_split = line.split(' ')
            # print(electric_split[0])
            # print(electric_split)
            for i, sign in enumerate(electric_split):
                # print(i, sign)
                if sign == nis and i < len(electric_split) - 1 and electric_split[i + 1].replace('.', '', 1).isdigit():
                    electric += float(electric_split[i + 1])
        if 'מים' in line.split(' '):
            water_split = line.split(' ')
            for i, sign in enumerate(water_split):
                if sign == nis and i < len(electric_split) - 1 and water_split[i + 1].replace('.', '', 1).isnumeric():
                    water += float(water_split[i + 1])
    return electric, water


def read_bill(file_name, date) -> dict:
    # creating a pdf file object
    pdfFileObj = open(file_name, 'rb')

    # creating a pdf reader object
    pdfReader = PyPDF2.PdfReader(pdfFileObj)

    # printing number of pages in pdf file
    tuple_bill = ()
    for i in range(len(pdfReader.pages)):
        pageObj = pdfReader.pages[i]
        tuple_bill = parse_bill(pageObj)
        if parse_bill(pageObj) != (0, 0):
            tuple_bill

    # closing the pdf file object
    pdfFileObj.close()
