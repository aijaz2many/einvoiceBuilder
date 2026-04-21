import fitz
from datetime import datetime

class MockData:
    def __init__(self):
        self.businessId = 1
        self.invoiceNumber = "INVC-0001"
        self.BookNo = "1"
        self.invoiceDate = "2026-04-21"
        self.CustomerName = "John Doe"
        self.amountinwords = "One Hundred Only"
        self.invoiceAmount = 100
        self.purpose = "Testing"
        self.billCollector = "Collector"
        self.Nazim = "Manager"
        self.customerFullAddress = "123 Street, City"
        self.customerPhone = "1234567890"
        self.paymentMode = "Cash"
        self.paymentType = "Full"

def generate_default_pdf(data, business) -> bytes:
    try:
        doc = fitz.open()
        page = doc.new_page(width=600, height=320)
        
        ORANGE = (1, 0.45, 0.1)
        DARK_BLUE = (0.1, 0.1, 0.3)
        GRAY = (0.4, 0.4, 0.4)
        TEXT_COLOR = (0.1, 0.1, 0.1)
        
        page.draw_rect(fitz.Rect(10, 10, 590, 310), color=(0.8, 0.8, 0.8), width=1)
        page.insert_text((180, 50), "CASH RECEIPT", fontsize=28, fontname="helv-bold", color=DARK_BLUE)
        
        info_x_start = 400
        info_x_end = 570
        y_start = 30
        line_v_spacing = 18
        
        display_date = data.invoiceDate
        if "-" in display_date:
            try:
                dt_obj = datetime.strptime(data.invoiceDate, "%Y-%m-%d")
                display_date = dt_obj.strftime("%d/%m/%Y")
            except:
                pass

        labels = ["NO.", "DATE", "MODE", "AMOUNT"]
        values = [
            data.invoiceNumber,
            display_date,
            data.paymentMode,
            f"Rs. {data.invoiceAmount:,.2f}"
        ]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            y = y_start + (i * line_v_spacing)
            page.insert_text((info_x_start, y), label, fontsize=9, fontname="helv-bold", color=GRAY)
            rect = fitz.Rect(info_x_start + 60, y - 10, info_x_end, y + 5)
            # align = fitz.TEXT_ALIGN_RIGHT (2)
            page.insert_textbox(rect, str(value), fontsize=10, fontname="helv", color=TEXT_COLOR, align=2)

        page.insert_text((35, 95), "RECEIVED FROM", fontsize=10, fontname="helv-bold", color=GRAY)
        page.insert_text((35, 120), data.CustomerName, fontsize=14, fontname="helv-bold", color=TEXT_COLOR)
        
        addr = data.customerFullAddress or ""
        if addr:
            rect = fitz.Rect(35, 130, 280, 180)
            page.insert_textbox(rect, addr, fontsize=10, fontname="helv", color=GRAY, align=0)

        body_y = 200
        page.insert_text((35, body_y), "FOR:", fontsize=10, fontname="helv-bold", color=GRAY)
        page.insert_text((130, body_y), data.purpose or "N/A", fontsize=12, fontname="helv", color=TEXT_COLOR)
        page.draw_line((130, body_y + 3), (550, body_y + 3), color=ORANGE, width=1)
        
        page.insert_text((35, body_y + 45), "RECEIVED BY:", fontsize=10, fontname="helv-bold", color=GRAY)
        biz_name = business.get("businessName", "N/A")
        page.insert_text((130, body_y + 45), biz_name, fontsize=12, fontname="helv", color=TEXT_COLOR)
        page.draw_line((130, body_y + 48), (550, body_y + 48), color=ORANGE, width=1)
        
        sig_name = data.Nazim or data.billCollector
        if sig_name:
            rect = fitz.Rect(420, 240, 570, 280)
            page.insert_textbox(rect, sig_name, fontsize=20, fontname="helv-bolditalic", color=DARK_BLUE, align=1)
            page.draw_line((430, 282), (560, 282), color=TEXT_COLOR, width=0.5)
            page.insert_text((475, 295), "Signature", fontsize=8, fontname="helv", color=GRAY)
        
        page.insert_text((35, 303), f"Book No: {data.BookNo}", fontsize=8, fontname="helv", color=GRAY)
        if data.customerPhone:
            page.insert_text((150, 303), f"Phone: {data.customerPhone}", fontsize=8, fontname="helv", color=GRAY)
        
        pdf_bytes = doc.write()
        doc.close()
        return pdf_bytes
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    data = MockData()
    business = {"businessName": "Test Business"}
    result = generate_default_pdf(data, business)
    if result:
        print("PDF generated successfully!")
        with open("test_output.pdf", "wb") as f:
            f.write(result)
    else:
        print("Failed to generate PDF.")
