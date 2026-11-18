import os
import sys
import json
import re
import html
import subprocess
import nbformat
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def markdown_to_html(md_text):
    """
    Converts standard notebook markdown to clean HTML.
    Handles headings, bold, italic, lists, code spans, blockquotes, and math.
    """
    lines = md_text.splitlines()
    html_lines = []
    in_list = False

    for line in lines:
        stripped = line.strip()

        # Empty line
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue

        # Headings
        if stripped.startswith('# '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            content = process_inline(stripped[2:])
            html_lines.append(f"<h1 class='nb-h1'>{content}</h1>")
            continue
        elif stripped.startswith('## '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            content = process_inline(stripped[3:])
            html_lines.append(f"<h2 class='nb-h2'>{content}</h2>")
            continue
        elif stripped.startswith('### '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            content = process_inline(stripped[4:])
            html_lines.append(f"<h3 class='nb-h3'>{content}</h3>")
            continue
        elif stripped.startswith('#### '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            content = process_inline(stripped[5:])
            html_lines.append(f"<h4 class='nb-h4'>{content}</h4>")
            continue

        # Ordered list items (e.g. 1. Question, 2. Question)
        m_ord = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if m_ord:
            if in_list:
                html_lines.append("</ul>"); in_list = False
            num = m_ord.group(1)
            content = process_inline(m_ord.group(2))
            html_lines.append(f"<p class='nb-p' style='margin-top: 10px; margin-bottom: 4px;'><strong>{num}.</strong> {content}</p>")
            continue

        # Unordered list
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                html_lines.append("<ul class='nb-ul'>")
                in_list = True
            content = process_inline(stripped[2:])
            html_lines.append(f"<li>{content}</li>")
            continue

        # Blockquote
        if stripped.startswith('> '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            content = process_inline(stripped[2:])
            html_lines.append(f"<blockquote class='nb-quote'>{content}</blockquote>")
            continue

        # Regular paragraph
        if in_list:
            html_lines.append("</ul>")
            in_list = False

        content = process_inline(line)
        html_lines.append(f"<p class='nb-p'>{content}</p>")

    if in_list:
        html_lines.append("</ul>")

    return "\n".join(html_lines)

def process_inline(text):
    """Handles inline formatting like bold, italics, code, links, math."""
    # Bold **text**
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic *text*
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    # Inline code `code`
    text = re.sub(r'`(.+?)`', r'<code class="inline-code">\1</code>', text)
    return text

def highlight_python_code(code_str):
    """Uses Pygments for syntax highlighting."""
    formatter = HtmlFormatter(nowrap=True)
    return highlight(code_str, PythonLexer(), formatter)

def notebook_to_html(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    filename = os.path.basename(nb_path)
    title = os.path.splitext(filename)[0].replace('_', ' ')

    pygments_css = HtmlFormatter(style='friendly').get_style_defs('.input-code')

    cells_html = []

    for cell in nb.cells:
        cell_type = cell.cell_type
        source = cell.source

        if cell_type == 'markdown':
            rendered_md = markdown_to_html(source)
            cells_html.append(f"""
            <div class="cell markdown-cell">
                {rendered_md}
            </div>
            """)

        elif cell_type == 'code':
            exec_count = cell.execution_count or ' '
            code_html = highlight_python_code(source)

            outputs_html = []
            for out in cell.get('outputs', []):
                out_type = out.get('output_type')

                # Text / stdout stream
                if out_type == 'stream':
                    text_out = html.escape(out.get('text', ''))
                    outputs_html.append(f"""
                    <div class="output-stream">
                        <pre>{text_out}</pre>
                    </div>
                    """)

                # Display data (images, HTML tables)
                elif out_type in ('display_data', 'execute_result'):
                    data = out.get('data', {})

                    # HTML (e.g. DataFrame table)
                    if 'text/html' in data:
                        html_table = data['text/html']
                        outputs_html.append(f"""
                        <div class="output-html">
                            {html_table}
                        </div>
                        """)
                    # Image PNG
                    elif 'image/png' in data:
                        b64_img = data['image/png']
                        outputs_html.append(f"""
                        <div class="output-image">
                            <img src="data:image/png;base64,{b64_img}" alt="Generated Plot" />
                        </div>
                        """)
                    # Fallback plain text
                    elif 'text/plain' in data:
                        plain_txt = html.escape(data['text/plain'])
                        outputs_html.append(f"""
                        <div class="output-plain">
                            <pre>{plain_txt}</pre>
                        </div>
                        """)

                # Error output
                elif out_type == 'error':
                    tb = html.escape("\n".join(out.get('traceback', [])))
                    outputs_html.append(f"""
                    <div class="output-error">
                        <pre>{tb}</pre>
                    </div>
                    """)

            all_outputs = "\n".join(outputs_html)
            output_container = f"""
            <div class="output-container">
                <div class="output-prompt">Out [{exec_count}]:</div>
                <div class="output-body">{all_outputs}</div>
            </div>
            """ if outputs_html else ""

            cells_html.append(f"""
            <div class="cell code-cell">
                <div class="input-container">
                    <div class="input-prompt">In [{exec_count}]:</div>
                    <div class="input-code">
                        <pre><code>{code_html}</code></pre>
                    </div>
                </div>
                {output_container}
            </div>
            """)

    cells_body = "\n".join(cells_html)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <!-- MathJax 3 configuration for math formulas -->
    <script>
    MathJax = {{
        tex: {{
            inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
            displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
        }},
        svg: {{ fontCache: 'global' }}
    }};
    </script>
    <script type="text/javascript" id="MathJax-script" async
        src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
    </script>
    <style>
        @page {{
            size: A4;
            margin: 14mm 14mm 14mm 14mm;
            @bottom-right {{
                content: counter(page);
            }}
        }}

        *, *::before, *::after {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            font-size: 10.5pt;
            line-height: 1.55;
            color: #1e293b;
            background-color: #ffffff;
            margin: 0;
            padding: 0;
        }}

        .notebook-wrapper {{
            max-width: 900px;
            margin: 0 auto;
            padding: 10px 20px 40px 20px;
        }}

        .doc-header {{
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 12px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
        }}

        .doc-badge {{
            font-size: 8.5pt;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            background: #eff6ff;
            color: #1d4ed8;
            padding: 4px 10px;
            border-radius: 4px;
            border: 1px solid #bfdbfe;
        }}

        /* Markdown styling */
        .nb-h1 {{
            font-size: 18pt;
            font-weight: 700;
            color: #0f172a;
            margin-top: 14px;
            margin-bottom: 12px;
            line-height: 1.3;
        }}

        .nb-h2 {{
            font-size: 13.5pt;
            font-weight: 600;
            color: #1e3a8a;
            margin-top: 20px;
            margin-bottom: 10px;
            border-bottom: 1px solid #e2e8f0;
            padding-bottom: 4px;
        }}

        .nb-h3 {{
            font-size: 11.5pt;
            font-weight: 600;
            color: #2563eb;
            margin-top: 16px;
            margin-bottom: 8px;
        }}

        .nb-p {{
            margin-top: 0;
            margin-bottom: 8px;
            color: #334155;
        }}

        .nb-ul {{
            margin-top: 4px;
            margin-bottom: 10px;
            padding-left: 22px;
        }}

        .nb-ul li {{
            margin-bottom: 4px;
            color: #334155;
        }}

        .nb-quote {{
            margin: 10px 0;
            padding: 8px 14px;
            border-left: 4px solid #3b82f6;
            background-color: #f8fafc;
            color: #475569;
            font-style: italic;
        }}

        .inline-code {{
            font-family: "Consolas", "Courier New", monospace;
            background: #f1f5f9;
            color: #dc2626;
            padding: 2px 5px;
            border-radius: 4px;
            font-size: 9.5pt;
            border: 1px solid #e2e8f0;
        }}

        /* Cells structure */
        .cell {{
            margin-bottom: 14px;
            page-break-inside: avoid;
        }}

        .code-cell {{
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            overflow: hidden;
            background-color: #ffffff;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 16px;
        }}

        .input-container {{
            display: flex;
            background-color: #f8fafc;
            border-bottom: 1px solid #e2e8f0;
        }}

        .input-prompt {{
            width: 70px;
            padding: 8px 6px;
            font-family: "Consolas", monospace;
            font-size: 8.5pt;
            color: #3b82f6;
            font-weight: 600;
            text-align: right;
            user-select: none;
            flex-shrink: 0;
        }}

        .input-code {{
            flex-grow: 1;
            padding: 6px 12px;
            overflow-x: hidden;
        }}

        .input-code pre {{
            margin: 0;
            font-family: "Consolas", "Menlo", "Courier New", monospace;
            font-size: 9pt;
            line-height: 1.45;
            color: #1e293b;
            white-space: pre-wrap;
            word-wrap: break-word;
            word-break: break-all;
        }}

        /* Pygments CSS */
        {pygments_css}

        /* Outputs */
        .output-container {{
            display: flex;
            background-color: #ffffff;
            padding: 4px 0;
        }}

        .output-prompt {{
            width: 70px;
            padding: 8px 6px;
            font-family: "Consolas", monospace;
            font-size: 8.5pt;
            color: #dc2626;
            font-weight: 600;
            text-align: right;
            user-select: none;
            flex-shrink: 0;
        }}

        .output-body {{
            flex-grow: 1;
            padding: 4px 12px;
            overflow-x: hidden;
        }}

        .output-stream pre {{
            margin: 0 0 6px 0;
            font-family: "Consolas", monospace;
            font-size: 8.5pt;
            color: #1e293b;
            white-space: pre-wrap;
            word-wrap: break-word;
            background-color: #f8fafc;
            padding: 6px 10px;
            border-radius: 4px;
            border: 1px solid #e2e8f0;
        }}

        .output-plain pre {{
            margin: 0;
            font-family: "Consolas", monospace;
            font-size: 8.5pt;
            color: #334155;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .output-image {{
            margin: 8px 0;
            text-align: center;
        }}

        .output-image img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }}

        /* Pandas DataFrame HTML tables */
        .output-html {{
            margin: 8px 0;
            overflow-x: auto;
        }}

        table.dataframe {{
            border-collapse: collapse;
            font-size: 8.5pt;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            width: 100%;
            border: 1px solid #cbd5e1;
        }}

        table.dataframe th, table.dataframe td {{
            padding: 5px 9px;
            border: 1px solid #e2e8f0;
            text-align: right;
        }}

        table.dataframe th {{
            background-color: #f8fafc;
            font-weight: 600;
            color: #1e293b;
            text-align: center;
        }}

        table.dataframe tr:nth-child(even) {{
            background-color: #f8fafc;
        }}

        /* Print Specific */
        @media print {{
            body {{
                font-size: 9.5pt;
            }}
            .code-cell {{
                box-shadow: none;
                border-color: #cbd5e1;
            }}
            .cell {{
                page-break-inside: avoid;
            }}
            .output-image img {{
                max-width: 95%;
            }}
        }}
    </style>
</head>
<body>
    <div class="notebook-wrapper">
        <div class="doc-header">
            <div>
                <span class="doc-badge">Machine Learning Lab • Executed Notebook</span>
            </div>
            <div style="font-size: 8.5pt; color: #64748b;">
                Dataset: <code>Crop_recommendation.csv</code> (2,200 rows)
            </div>
        </div>
        {cells_body}
    </div>
</body>
</html>
"""
    return full_html

def convert_notebook_to_pdf(nb_path, output_pdf=None):
    if not os.path.exists(nb_path):
        raise FileNotFoundError(f"Notebook not found: {nb_path}")

    if output_pdf is None:
        base_name = os.path.splitext(nb_path)[0]
        output_pdf = base_name + ".pdf"

    abs_output_pdf = os.path.abspath(output_pdf)
    html_content = notebook_to_html(nb_path)

    temp_html = os.path.splitext(nb_path)[0] + "_temp_render.html"
    abs_temp_html = os.path.abspath(temp_html)

    with open(abs_temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[HTML] Rendered notebook to HTML: {abs_temp_html}")

    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    ]
    browser_exe = None
    for p in edge_paths:
        if os.path.exists(p):
            browser_exe = p
            break

    if not browser_exe:
        raise RuntimeError("No compatible headless browser (Edge or Chrome) found.")

    print(f"[PDF] Converting using headless browser: {os.path.basename(browser_exe)} ...")
    cmd = [
        browser_exe,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={abs_output_pdf}",
        abs_temp_html
    ]

    res = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(abs_output_pdf) and os.path.getsize(abs_output_pdf) > 0:
        pdf_size = os.path.getsize(abs_output_pdf)
        print(f"[SUCCESS] PDF generated successfully!")
        print(f"  Path: {abs_output_pdf}")
        print(f"  Size: {pdf_size:,} bytes")
        try:
            os.remove(abs_temp_html)
        except Exception:
            pass
        return abs_output_pdf
    else:
        print("[ERROR] PDF generation failed.")
        print("Stdout:", res.stdout)
        print("Stderr:", res.stderr)
        return None

if __name__ == "__main__":
    target_nb = sys.argv[1] if len(sys.argv) > 1 else "Tutorial_10_Hierarchical_Clustering.ipynb"
    convert_notebook_to_pdf(target_nb)
