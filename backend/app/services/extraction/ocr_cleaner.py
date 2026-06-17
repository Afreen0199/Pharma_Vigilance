import re

def clean_ocr_text(text: str) -> str:
    """
    Cleans OCR-extracted text by removing artifacts, normalizing line breaks, 
    fixing word splits, and improving overall medical text structure.
    """
    if not text:
        return ""

    # 1. Clean weird characters and common OCR noise symbols
    # Often scan lines/boxes appear as | _ [ ] ~ \
    cleaned = re.sub(r'[\\|~_^]+', ' ', text)

    # 2. Normalize horizontal spacing (convert multiple spaces or tabs to a single space)
    cleaned = re.sub(r'[ \t]+', ' ', cleaned)

    # 3. Standardize line endings and remove carriage returns
    cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')

    # 4. Handle split words at the end of lines (e.g. "hepa-\ntotoxicity" -> "hepatotoxicity")
    cleaned = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', cleaned)

    # 5. Handle lines that split sentences unnecessarily
    # If a line does not end with terminal punctuation (. ? ! :) and the next line starts with lowercase, combine them
    lines = cleaned.split('\n')
    combined_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            combined_lines.append("")
            i += 1
            continue
        
        # Look ahead to next line if there is one
        while i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if not next_line:
                break
            
            # Conditions for combining:
            # - Current line doesn't end in typical terminal punctuation (. ? ! : ;)
            # - Next line starts with a lowercase letter, digit, or common continuation character
            ends_open = not line.endswith(('.', '?', '!', ':', ';'))
            starts_continuation = next_line[0].islower() or next_line[0].isdigit() or next_line[0] in (',', ')')
            
            if ends_open and starts_continuation:
                line = line + " " + next_line
                i += 1
            else:
                break
        
        combined_lines.append(line)
        i += 1

    # 6. Re-assemble and normalize vertical spacing (remove excessive consecutive newlines)
    cleaned = '\n'.join(combined_lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

    return cleaned.strip()
