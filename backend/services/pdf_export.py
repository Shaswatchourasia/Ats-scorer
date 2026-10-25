# import io
# import logging

# try:
#     from weasyprint import HTML, CSS
#     WEASYPRINT_INSTALLED = True
# except ImportError:
#     WEASYPRINT_INSTALLED = False

# logger = logging.getLogger('ats_resume_scorer')

# def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
#     if not WEASYPRINT_INSTALLED:
#         raise ImportError("WeasyPrint is not installed. PDF generation unavailable.")
        
#     documents = []
    
#     # Render all 3 HTML strings to WeasyPrint Document objects
#     for name, html_str in html_docs.items():
#         doc = HTML(string=html_str).render()
#         documents.append(doc)
    
#     # Merge them into the first document
#     first_doc = documents[0]
#     for other_doc in documents[1:]:
#         for page in other_doc.pages:
#             first_doc.pages.append(page)
            
#     # Write combined PDF bytes
#     pdf_bytes = first_doc.write_pdf()
#     return pdf_bytes

# # ```python  given by chatgpt
# from io import BytesIO

# from playwright.async_api import async_playwright
# from pypdf import PdfReader, PdfWriter


# async def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
#     """Convert multiple HTML reports into one PDF using Playwright."""

#     if not html_docs:
#         raise ValueError("No HTML reports were provided.")

#     writer = PdfWriter()

#     async with async_playwright() as playwright:
#         browser = await playwright.chromium.launch()

#         try:
#             for name, html_content in html_docs.items():
#                 page = await browser.new_page()

#                 try:
#                     await page.set_content(
#                         html_content,
#                         wait_until="load",
#                     )

#                     pdf_bytes = await page.pdf(
#                         format="A4",
#                         print_background=True,
#                     )

#                     reader = PdfReader(BytesIO(pdf_bytes))

#                     for pdf_page in reader.pages:
#                         writer.add_page(pdf_page)

#                 finally:
#                     await page.close()

#         finally:
#             await browser.close()

#     output = BytesIO()
#     writer.write(output)

#     return output.getvalue()

from io import BytesIO

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter


def generate_combined_pdf(html_docs: dict[str, str]) -> bytes:
    """Convert HTML reports into one PDF."""

    if not html_docs:
        raise ValueError("No HTML reports were provided.")

    writer = PdfWriter()

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()

        try:
            for name, html_content in html_docs.items():
                page = browser.new_page()

                try:
                    page.set_content(html_content, wait_until="load")

                    pdf_bytes = page.pdf(
                        format="A4",
                        print_background=True,
                    )

                    reader = PdfReader(BytesIO(pdf_bytes))

                    for pdf_page in reader.pages:
                        writer.add_page(pdf_page)

                finally:
                    page.close()

        finally:
            browser.close()

    output = BytesIO()
    writer.write(output)

    return output.getvalue()