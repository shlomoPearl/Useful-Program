import PyPDF2
from io import BytesIO

nis = "\u20AA"


class ReadBill:
    def __init__(self, date_data_dict: dict):
        self.date_data_dict = date_data_dict

    def parser(self, parse_key):
        bill_dict = {}
        for date in self.date_data_dict.keys():
            bill_dict[date] = 0
            pdf_data = BytesIO(self.date_data_dict.get(date))
            pdf_file = PyPDF2.PdfReader(pdf_data)
            for page in pdf_file.pages:
                text = page.extract_text()
                lines = text.split('\n')
                for line in lines:
                    line_split = line.split(' ')
                    if parse_key in line_split:
                        for i, sign in enumerate(line_split):
                            if sign == nis and i < len(line_split) - 1 and \
                                    line_split[i + 1].replace('.', '', 1).isdigit():
                                bill_dict[date] += float(line_split[i + 1])
        return bill_dict
