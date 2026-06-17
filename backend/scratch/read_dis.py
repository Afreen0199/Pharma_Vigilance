import re

with open("/Users/affu01/GRAD_PROJ_NEW/backend/scratch/report_service_dis.txt", "r") as f:
    text = f.read()

pos = text.find("Disassembly of <code object generate_pdf_report")
if pos == -1:
    print("Method not found")
    exit()

end_pos = text.find("Disassembly of", pos + 1)
method_dis = text[pos:end_pos] if end_pos != -1 else text[pos:]

lines = method_dis.split("\n")
instrs = []
current_line = None

for l in lines:
    m_line = re.match(r"^\s*(\d+)\s+(\d+)\s+(\w+)\s*(.*)$", l)
    if m_line:
        current_line = int(m_line.group(1))
        offset = int(m_line.group(2))
        op = m_line.group(3)
        args = m_line.group(4)
        instrs.append((current_line, offset, op, args))
    else:
        m_no_line = re.match(r"^\s*(\d+)\s+(\w+)\s*(.*)$", l)
        if m_no_line:
            offset = int(m_no_line.group(1))
            op = m_no_line.group(2)
            args = m_no_line.group(3)
            instrs.append((current_line, offset, op, args))

print("String constants in generate_pdf_report:")
for line, offset, op, args in instrs:
    if op == "LOAD_CONST":
        m_val = re.search(r"\((.*?)\)", args)
        if m_val:
            val = m_val.group(1)
            # If it is a string constant
            if val.startswith("'") and val.endswith("'") or val.startswith('"') and val.endswith('"'):
                print(f"Line {line} (offset {offset}): {val}")
