# -*- coding: utf-8 -*-
"""
Created on Tue Aug 12 11:37:01 2025

@author: Allen Jones
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug  5 13:20:32 2025

@author: Allen Jones

Script to scrape out only the main body of a dissertation in (PDF) so I can listen to it while riding.
"""

import fitz  # PyMuPDF

# --- Configuration ---
INPUT_PDF = "Nika Spaulding DMin Thesis FINAL.pdf"
OUTPUT_PDF = "spaulding_clean.pdf" # The name of the new, clean file
FOOTNOTE_SIZE = 10.0  # The font size of footnotes
BODY_SIZE = 12.0      # The font size of your main text and page numbers
FOOTER_MARGIN = 72    # How many points from the bottom to consider the "footer area" (72 points = 1 inch)

def is_page_number(block_text, y_pos, page_height):
    """
    Checks if a block of text is likely a page number.
    It must be in the footer area and contain only digits.
    """
    # Check 1: Is the text block in the footer area?
    if y_pos < (page_height - FOOTER_MARGIN):
        return False
        
    # Check 2: Is the text content just a number?
    # Strips any whitespace and checks if the result is all digits.
    if not block_text.strip().isdigit():
        return False
        
    return True

def clean_dissertation_page(page, new_page):
    """
    Processes a single page, copying only the main body text.
    """
    # Get all text blocks with detailed information
    blocks = page.get_text("dict")["blocks"]
    
    # Get all drawing elements to find the footnote separator line
    drawings = page.get_drawings()
    
    footnote_line_y = 0
    # Find the horizontal line that separates footnotes
    for path in drawings:
        # A simple horizontal line is a path with two points with the same y-coordinate
        if len(path['items']) == 2 and path['items'][0][0] == 'l':
             p1 = path['items'][0][1]
             p2 = path['items'][1]
             # Check if it's a horizontal line (y-coordinates are very close)
             if abs(p1.y - p2.y) < 1:
                  # We only care about the first one we find from the top
                  if p1.y > footnote_line_y:
                      footnote_line_y = p1.y

    # Iterate through each text block on the page
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = round(span["size"])
                    text = span["text"]
                    origin_y = span["origin"][1] # The vertical position of the text
                    
                    # --- APPLY OUR RULES ---
                    
                    # Rule 1: Is it a footnote? Check the font size.
                    # As an extra check, if we found a separator line, we only
                    # count text below it as a potential footnote.
                    is_footnote = (font_size == FOOTNOTE_SIZE)
                    if footnote_line_y > 0 and origin_y < footnote_line_y:
                        is_footnote = False # It's 10pt font, but above the line, so keep it.

                    # Rule 2: Is it a page number?
                    is_p_num = (font_size == BODY_SIZE) and is_page_number(text, origin_y, page.rect.height)

                    # --- DECISION ---
                    # If it's not a footnote and not a page number, we keep it.
                    if not is_footnote and not is_p_num:
                        
                        # NEW: Logic to select the correct built-in font variant
                        flags = span['flags']
                        is_italic = flags & 1
                        is_bold = flags & 2
                        
                        font_name = "timo"  # Default: Times Roman
                        if is_bold and is_italic:
                            font_name = "tibi"  # Times Bold Italic
                        elif is_bold:
                            font_name = "tibo"  # Times Bold
                        elif is_italic:
                            font_name = "tiit"  # Times Italic

                        # Insert the clean text into the new page using the determined font
                        new_page.insert_text(span["origin"],
                                             text,
                                             fontname=font_name,
                                             fontsize=span["size"],
                                             color=span["color"])

def main():
    """Main function to run the PDF cleaning process."""
    try:
        doc = fitz.open(INPUT_PDF)
    except Exception as e:
        print(f"Error opening file! Make sure '{INPUT_PDF}' is in the same folder as the script.")
        print(f"Details: {e}")
        return

    new_doc = fitz.open()  # Create a new, empty PDF
    
    print(f"Processing '{INPUT_PDF}'...")
    
    # Process each page
    for i, page in enumerate(doc):
        print(f"  - Cleaning page {i+1}/{len(doc)}")
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        clean_dissertation_page(page, new_page)
        
    print(f"Saving cleaned file to '{OUTPUT_PDF}'...")
    new_doc.save(OUTPUT_PDF, garbage=4, deflate=True)
    new_doc.close()
    doc.close()
    print("Done!")

if __name__ == "__main__":
    main()