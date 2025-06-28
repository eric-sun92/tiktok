import http.client
import json        

conn = http.client.HTTPSConnection("tiktok-download-without-watermark.p.rapidapi.com")

headers = {
    "x-rapidapi-key":  "18f4ee360cmsha13f52eb8669e31p16c4f6jsn318a788d3b76",
    "x-rapidapi-host": "tiktok-download-without-watermark.p.rapidapi.com",
}

link = "www.tiktok.com/@italicque/video/7519585162250734870?q=sparks&t=1751081144432"
prefix = "/analysis?url=https%3A%2F%2F"
total = prefix + link

conn.request(
    "GET",
    total,
    headers=headers,
)

res  = conn.getresponse()
raw  = res.read().decode("utf-8")    

parsed = json.loads(raw)             
pretty = json.dumps(parsed, indent=2, ensure_ascii=False)

out = "tiktok_output.json"
with open(out, "w", encoding="utf-8") as f:
    f.write(pretty)

print(f"Formatted JSON saved to {out}")