import os
import sys
import win32com.client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pptx_files = [
    os.path.join(BASE_DIR, "Review_2_Crop_Fertilizer_ML.pptx"),
    os.path.join(BASE_DIR, "Comprehensive_Viva_Crop_Fertilizer_ML copy.pptx")
]

powerpoint = win32com.client.Dispatch("PowerPoint.Application")

for pptx_path in pptx_files:
    pdf_path = os.path.splitext(pptx_path)[0] + ".pdf"
    print(f"[INFO] Converting {os.path.basename(pptx_path)} to PDF...")
    deck = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
    # 32 = ppSaveAsPDF
    deck.SaveAs(pdf_path, 32)
    deck.Close()
    print(f"[OK] Generated {pdf_path} (Size: {os.path.getsize(pdf_path):,} bytes)")

powerpoint.Quit()
print("[ALL DONE] PDF generation complete.")

