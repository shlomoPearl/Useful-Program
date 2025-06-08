import re

import PyPDF2
from io import BytesIO


# Clean and validate amount string
def clean_amount_string(amount_str):
    if not amount_str:
        return None
    cleaned = amount_str.replace(',', '').strip()
    try:
        if re.match(r'^\d+\.?\d*$', cleaned):
            return float(cleaned)
    except ValueError:
        pass
    return None


class ReadBill:
    def __init__(self, date_data_dict: dict, currency_symbols):
        self.date_data_dict = date_data_dict
        self.currency_symbols = currency_symbols

    def extract_amounts_from_line(self, line, parse_key=None):
        amounts = []
        if parse_key and parse_key.lower() not in line.lower():
            return amounts
        line_split = line.split(' ')
        for i, token in enumerate(line_split):
            if isinstance(self.currency_symbols, list):
                currency_match = any(token.lower() == symbol.lower() for symbol in self.currency_symbols)
            else:
                currency_match = token.lower() == self.currency_symbols.lower()
            if currency_match and i < len(line_split) - 1:
                potential_amount = line_split[i + 1]
                cleaned_amount = clean_amount_string(potential_amount)
                if cleaned_amount is not None:
                    amounts.append(cleaned_amount)
        for i, token in enumerate(line_split):
            cleaned_amount = clean_amount_string(token)
            if cleaned_amount is not None and i < len(line_split) - 1:
                next_token = line_split[i + 1]
                if isinstance(self.currency_symbols, list):
                    currency_match = any(next_token.lower() == symbol.lower() for symbol in self.currency_symbols)
                else:
                    currency_match = next_token.lower() == self.currency_symbols.lower()
                if currency_match:
                    amounts.append(cleaned_amount)
        return amounts

    def parser(self, parse_key=None):
        bill_dict = {}
        for date in self.date_data_dict.keys():
            bill_dict[date] = 0.0
            try:
                pdf_data = BytesIO(self.date_data_dict.get(date))
                if not pdf_data.getvalue():
                    continue
                pdf_file = PyPDF2.PdfReader(pdf_data)
                if len(pdf_file.pages) == 0:
                    continue
                for page_num, page in enumerate(pdf_file.pages):
                    try:
                        text = page.extract_text()
                        if not text.strip():
                            continue
                        lines = text.split('\n')
                        page_total = 0.0
                        for line in lines:
                            if line.strip():  # Skip empty lines
                                amounts = self.extract_amounts_from_line(line, parse_key)
                                page_total += sum(amounts)
                        bill_dict[date] += page_total
                    except Exception as e:
                        continue
            except Exception as e:
                continue
        print("bill dict-", bill_dict)
        return bill_dict
