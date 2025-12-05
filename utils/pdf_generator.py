import io
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from datetime import datetime

def generate_receipt_pdf(user_name, expenses):
    """
    Generates a PDF receipt looking like a thermal printout.
    Returns a BytesIO object containing the PDF data.
    """

    width = 80 * mm
    height = (150 + (len(expenses) * 10)) * mm 
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    def draw_centered(text, y, font_size=10, font="Courier-Bold"):
        c.setFont(font, font_size)
        text_width = c.stringWidth(text, font, font_size)
        c.drawString((width - text_width) / 2, y, text)

    def draw_line(y):
        c.setDash(3, 3) # 3 points on, 3 off
        c.line(5 * mm, y, 75 * mm, y)
        c.setDash([]) # Reset to solid

    
    y = height - 15 * mm # Start from top
    
    # Header
    draw_centered("BUDGET TRACKER BOT", y, 12)
    y -= 5 * mm
    draw_centered(f"User: {user_name}", y, 8, "Courier")
    y -= 5 * mm
    draw_centered(datetime.now().strftime("%Y-%m-%d %H:%M"), y, 8, "Courier")
    
    y -= 8 * mm
    draw_centered("********************************", y, 8, "Courier")
    y -= 5 * mm
    draw_centered("CASH RECEIPT", y, 14, "Courier-Bold")
    y -= 5 * mm
    draw_centered("********************************", y, 8, "Courier")
    
    y -= 10 * mm
    
    # Table Headers
    c.setFont("Courier-Bold", 9)
    c.drawString(5 * mm, y, "Description")
    c.drawRightString(75 * mm, y, "Price")
    
    y -= 3 * mm
    draw_line(y)
    y -= 5 * mm
    
    # Expenses Loop
    total = 0.0
    c.setFont("Courier", 9)
    
    for exp in expenses:
        # Truncate category if too long
        cat_name = (exp.category[:15] + '..') if len(exp.category) > 15 else exp.category
        price_str = f"{exp.amount:.2f}"
        
        c.drawString(5 * mm, y, cat_name)
        c.drawRightString(75 * mm, y, price_str)
        
        total += exp.amount
        y -= 5 * mm # Move down for next item

    y -= 2 * mm
    draw_line(y)
    y -= 6 * mm
    
    # Total
    c.setFont("Courier-Bold", 14)
    c.drawString(5 * mm, y, "Total")
    c.drawRightString(75 * mm, y, f"${total:.2f}")
    
    y -= 10 * mm
    
    # Footer Info
    c.setFont("Courier", 8)
    c.drawString(5 * mm, y, "Cash")
    c.drawRightString(75 * mm, y, f"{total:.2f}")
    y -= 4 * mm
    c.drawString(5 * mm, y, "Change")
    c.drawRightString(75 * mm, y, "0.00")
    
    y -= 8 * mm
    draw_centered("********************************", y, 8, "Courier")
    y -= 5 * mm
    draw_centered("THANK YOU!", y, 10, "Courier-Bold")
    
    y -= 8 * mm
    draw_line(y)
    y -= 5 * mm

    c.drawString(5 * mm, y, "By : Tekleeyesus Munye")
    y -= 4 * mm
    c.drawString(5 * mm, y, "Email: tekleeyesus21@gmail.com")

    c.save()
    buffer.seek(0)
    return buffer