import http.client

conn = http.client.HTTPSConnection("tiktok-download-without-watermark.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "18f4ee360cmsha13f52eb8669e31p16c4f6jsn318a788d3b76",
    'x-rapidapi-host': "tiktok-download-without-watermark.p.rapidapi.com"
}

conn.request("GET", "/analysis?url=https%3A%2F%2Fwww.tiktok.com/@gillblanco/video/7384526401396821291?q=omikase%20%2033&t=1751078710588", headers=headers)


res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))