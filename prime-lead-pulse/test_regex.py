import re
labels = [
  "Google Account: Vicky (vickythakkar6143@gmail.com)",
  "Google Account: Vicky Thakkar (vickythakkar6143@gmail.com)",
  "Google Account: Vicky Thakkar \n(vickythakkar6143@gmail.com)"
]
for l in labels:
  match = re.search(r'\(([^)]+@[^)]+)\)', l)
  print(match.group(1) if match else "No match")
