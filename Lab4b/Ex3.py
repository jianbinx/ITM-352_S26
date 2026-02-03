url = input("Enter a FullURL: ")

cleaned_url = url.replace("http://", "")

print("Cleaned URL:", cleaned_url)

parts = cleaned_url.split(".")

domain = parts[1]
print("Domain:", domain)

TLD = parts[2]
TLD_cleaned = TLD.strip("/")
print("Top-Level Domain (TLD):", TLD_cleaned)
