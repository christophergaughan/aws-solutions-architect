import pikepdf

try:
    pdf = pikepdf.Pdf.open("20230408_flattened.pdf")
    print("No encryption detected. PDF seems valid.")
except pikepdf._qpdf.PasswordError:
    print("PDF is encrypted!")
except pikepdf._qpdf.Error as e:
    print(f"PDF is corrupt or invalid: {e}")

