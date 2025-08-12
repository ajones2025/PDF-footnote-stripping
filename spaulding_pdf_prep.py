# -*- coding: utf-8 -*-
"""
Created on Tue Aug  11 13:20:32 2025

@author: Allen Jones

Script to scrape out only the main body of a dissertation in (PDF) so I can listen to it while riding.
"""

import fitz  # PyMuPDF

# --- Configuration ---
INPUT_PDF = "Nika Spaulding DMin Thesis FINAL.pdf"  # CHANGE THIS if your input file name is different
OUTPUT_TEXT_FILE = "dissertation_clean.txt" # The name of the new, clean text file
FOOTNOTE_SIZE = 10.0  # The font size of your footnotes
BODY_SIZE = 12.0      # The font size of your main text and page numbers
FOOTER_MARGIN = 72    # How many points from the bottom to consider the "footer area" (72 points = 1 inch)

def is_page_number(block_text, y_pos, page_height):
    """
    Checks if a block of text is likely a page number.
    It must be in the footer area and contain only digits.
    """
    if y_pos < (page_height - FOOTER_MARGIN):
        return False
    if not block_text.strip().isdigit():
        return False
    return True

def get_clean_text_from_page(page):
    """
    Processes a single page, extracting only the main body text as a string.
    """
    page_text = ""  # A string to hold all the clean text from this page
    blocks = page.get_text("dict")["blocks"]
    
    
    for block in blocks:
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    font_size = round(span["size"])
                    text = span["text"]
                    origin_y = span["origin"][1]
                    
                    # --- APPLY OUR RULES ---
                    is_footnote = (font_size == FOOTNOTE_SIZE)
                    is_p_num = (font_size == BODY_SIZE) and is_page_number(text, origin_y, page.rect.height)

                    # --- DECISION ---
                    # If it's not a footnote and not a page number, we keep it.
                    if not is_footnote and not is_p_num:
                        # Add the clean text to our page string
                        page_text += text + " "
                
                # Add a new line character after each line of text to preserve paragraph breaks.
                if not is_footnote and not is_p_num:
                     page_text += "\n"
    
    return page_text

def main():
    """Main function to run the text extraction process."""
    try:
        doc = fitz.open(INPUT_PDF)
    except Exception as e:
        print(f"Error opening file! Make sure '{INPUT_PDF}' is in the same folder as the script.")
        print(f"Details: {e}")
        return

    full_clean_text = "" # A single string to hold the entire document's text
    
    print(f"Processing '{INPUT_PDF}'...")
    
    # Process each page
    for i, page in enumerate(doc):
        print(f"  - Cleaning page {i+1}/{len(doc)}")
        full_clean_text += get_clean_text_from_page(page) + "\n\n"
        
    print(f"Saving cleaned text to '{OUTPUT_TEXT_FILE}'...")
    
    # Write the final string to a text file
    with open(OUTPUT_TEXT_FILE, "w", encoding="utf-8") as text_file:
        text_file.write(full_clean_text)
        
    doc.close()
    print("Done! ✨")

if __name__ == "__main__":
    main()