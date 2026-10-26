import re

# 1. Map common OCR confusions between letters and numbers
N_TO_L = {'0': 'O', '1': 'I', '2': 'Z', '5': 'S', '8': 'B'}  # Number to Letter
L_TO_N = {'O': '0', 'I': '1', 'Z': '2', 'S': '5', 'B': '8', 'D': '0', 'G': '6'}  # Letter to Number

def clean_ocr_text(raw_text):
    """Removes spaces and non-alphanumeric junk characters."""
    if not raw_text:
        return ""
    # Convert to uppercase and strip out spaces/punctuation
    cleaned = re.sub(r'[^A-Z0-9]', '', raw_text.upper())
    return cleaned

def fix_indian_plate(plate_text):
    """
    Corrects OCR mistakes based on the standard Indian plate schema:
    Positions: State(2L) + District(2N) + Unique(1-2L) + Number(4N)
    Total length usually varies from 9 to 10 characters.
    """
    plate = clean_ocr_text(plate_text)
    
    # Fast exit if the plate is completely empty or way too short
    if len(plate) < 8:
        return plate
        
    plate_chars = list(plate)
    
    # --- Phase 1: Position-Based Character Swapping ---
    
    # First 2 characters MUST be letters (State Code: MH, DL, KA, etc.)
    for i in range(0, 2):
        if plate_chars[i] in N_TO_L:
            plate_chars[i] = N_TO_L[plate_chars[i]]
            
    # Next 2 characters MUST be numbers (District Code: 12, 01, etc.)
    for i in range(2, 4):
        if plate_chars[i] in L_TO_N:
            plate_chars[i] = L_TO_N[plate_chars[i]]
            
    # The LAST 4 characters MUST be numbers (e.g., 1234)
    # We look backward from the end of the list
    for i in range(-1, -5, -1):
        if plate_chars[i] in L_TO_N:
            plate_chars[i] = L_TO_N[plate_chars[i]]
            
    # The remaining middle characters (indices 4 to len-4) MUST be letters (e.g., AB, C)
    for i in range(4, len(plate_chars) - 4):
        if plate_chars[i] in N_TO_L:
            plate_chars[i] = N_TO_L[plate_chars[i]]

    final_plate = "".join(plate_chars)
    
    # --- Phase 2: Format Validation using Regex ---
    # Matches: 2 Letters + 2 Numbers + 1 or 2 Letters + 4 Numbers
    indian_plate_pattern = r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$'
    
    if re.match(indian_plate_pattern, final_plate):
        return final_plate, True  # Validated
    else:
        return final_plate, False # Fixed but doesn't strictly match format

# --- Example Usage ---
ocr_outputs = [
    "MH 12 oB 1234",   # Mistake: 'o' instead of 'A/B' or number issue
    "DL0I AM S678",    # Mistakes: '0I' (should be 01), 'S' (should be 5)
    "KA.52.Z.88B8"     # Mistakes: Junk dots, 'B' instead of 8
]

print("--- ANPR Post-Processing Results ---")
for raw in ocr_outputs:
    corrected, is_valid = fix_indian_plate(raw)
    status = "✅ VALID" if is_valid else "⚠️ INVALID FORMAT"
    print(r"Raw:  '{:<15}' -> Fixed: '{:<10}' [{}]".format(raw, corrected, status))