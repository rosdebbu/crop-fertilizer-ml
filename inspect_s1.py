import pptx
prs = pptx.Presentation('Comprehensive_Viva_Crop_Fertilizer_ML.pptx')
s1 = prs.slides[0]
for idx, shp in enumerate(s1.shapes):
    print(f"Shape {idx}: [{shp.name}] ({shp.shape_type}) L={shp.left/914400:.2f}, T={shp.top/914400:.2f}, W={shp.width/914400:.2f}, H={shp.height/914400:.2f}")
    if shp.has_text_frame:
        for p_idx, p in enumerate(shp.text_frame.paragraphs):
            c = "None"
            if p.font.color and p.font.color.type == 1:
                c = str(p.font.color.rgb)
            print(f'   P{p_idx}: "{p.text}" (Font={p.font.name}, Sz={p.font.size}, Bold={p.font.bold}, Color={c})')

