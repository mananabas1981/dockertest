from openpyxl import load_workbook, Workbook
from openpyxl.styles import Alignment, Border, Side, Font 
from os import sep
from io import BytesIO
from base64 import b64encode


class RemittanceInputForm:
    def __init__(self):
        pass

    


class RemittanceStandardPrint:
    def __init__(self, file_type = 'html', data = None):
        '''
            @type -> html, excel, csv, pdf
        '''
        self.type = file_type # 
        self.data = data
        self.t = ''''''

    
    
    def init(self) -> bool:
        if (self.type == 'html'):
            self._html()

        elif self.type == "excel":
            self._excel()
        else:
            return False
        
        return True

    def _excel(self):
        wb = Workbook()

        # workbook = load_workbook(filename=f'data{os.sep}template{os.sep}ada.xlsx')

        # # Select the active worksheet
        # ws = workbook.worksheets[0]

        # grab the active worksheet
        ws = wb.active

        # Data can be assigned directly to cells
        # ws['A1'] = 42

        # # Rows can also be appended
        # ws.append([1, 2, 3])

        # # Python types will automatically be converted
        # import datetime
        # ws['A2'] = datetime.datetime.now()
        data = self.data
        
        # header   
        if not data:
            self.t = t
            return 
        
        header = data[0]["item"]
        if not header:
            self.t = t
            return
        i = 1

        ws[f"A{i}"] = f'{header[0]["code"]} Number'
        ws[f"B{i}"] = f'Lastname'
        ws[f"C{i}"] = f'Firstname'
        ws[f"D{i}"] = f'Middlename'
        ws[f"E{i}"] = f'Ext Name'
        
        char = "F"
        for item in header:
            ws[f"{char}{i}"] = item["name"]
            char = chr(ord(char) + 1)

        i += 1
        for _item in data:
            info = _item["name"]
            item = _item['item']
            ws[f'A{i}'] = "" # code here of the employee
            ws[f'B{i}'] = info["l"].upper()
            ws[f'C{i}'] = info['f'].upper()
            ws[f'D{i}'] = info['m'].upper()
            ws[f'E{i}'] = info['e'].upper()
            
            # value
            char = "F"
            for jitem in item:
                ws[f"{char}{i}"] = jitem["value"]
                char = chr(ord(char) + 1)
            # end value


            i += 1

        # Save the file
        by_io = BytesIO()
        # wb.save(f"data{sep}tmp{sep}sample.xlsx")
        wb.save(by_io)
        excel_data = by_io.getvalue()
        by_io.close()

        self.t = b64encode(excel_data).decode()

    def _html(self):
        t = '''
             <style>
                .table0 {
                    border-collapse: collapse;
                    width: 100%;
                }

                .table0 tr th,.table0 tr td {
                    text-align: left;
                    padding: 8px;
                    border: 1px solid black;
                }

                .table0 tr:nth-child(even) {
                    background-color: #f2f2f2;
                }
            </style>
        '''
        
        data = self.data
        
        # header   
        if not data:
            self.t = t
            return 
        
        header = data[0]["item"]
        if not header:
            self.t = t
            return
        
        t += f"""<table class="table0"><tr>"""
        t += f"""<td>{header[0]["code"]} Number</td>"""
        t += f"""<td>Fullname</td>"""
        for item in header:
            t += f"""<td>{item["name"]}</td>"""
        t += f"""</tr>"""

        for _item in data:

            t += "<tr>"
            info = _item["name"]
            item = _item["item"]
            t += "<td></td>"
            t += f"""<td>
                    {info["l"].upper()}, {info["f"].upper()} {info["e"].upper()}{info["m"].upper()}
            </td>"""

            for ded_item in item:
                t += f"""<td>{ded_item["value"]}</td>"""
            t += "</tr>"        
        

        t += """</table>"""
        self.t = t

    def output(self):        
        if self.type == 'html':
            return self.t
        
        if self.type == "excel":
            return self.t

        return None

