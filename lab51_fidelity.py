import re
path = r"F:\PORIDHI_JOB\labs\Data Quality for ML labs\lab 5.1\lab_5.1.md"
text = open(path, encoding="utf-8").read()

xml = re.findall(r"```xml\n(.*?)```", text, re.S)[0]

# every file path mentioned anywhere in the lab
paths = set(re.findall(r"[A-Za-z0-9_./-]+\.(?:csv|py|yaml|yml)", text))
print("=== files referenced in the lab text ===")
for p in sorted(paths):
    print("  ", p)

print("\n=== file names appearing as diagram labels ===")
# diagram labels
labels = re.findall(r'value="&lt;b&gt;([^<]+)&lt;/b&gt;', xml) + re.findall(r'value="([^"&]*\.(?:csv|py|yaml))"', xml)
for l in sorted(set(labels)):
    print("  ", l)

print("\n=== folder structure block ===")
fs = re.search(r"### Folder Structure.*?```text\n(.*?)```", text, re.S).group(1)
print(fs)

print("\n=== Architecture Structure preview ===")
a = re.search(r"### Architecture Structure.*?```text\n(.*?)```", text, re.S).group(1)
print(a)

print("\n=== components named in Architecture Explanation ===")
exp = re.search(r"### Architecture Explanation\n(.*?)\n## Learning Objectives", text, re.S).group(1)
print(exp[:2500])

print("\n=== six dimensions mentioned in diagram vs lab ===")
dims = ["Accuracy","Completeness","Consistency","Timeliness","Uniqueness","Validity"]
for d in dims:
    print(f"  {d}: diagram={d in xml}  lab_text={d in text}")

print("\n=== steps in lab ===")
for m in re.findall(r"^### (Step .*)$", text, re.M):
    print("  ", m)

print("\n=== commands actually run in lab ===")
for m in re.findall(r"```bash\n(.*?)```", text, re.S):
    print("  ---")
    print("   ", m.replace("\n","\n    "))
