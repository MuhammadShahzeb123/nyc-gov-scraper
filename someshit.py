import requests

url = "https://a836-citypay.nyc.gov/citypay/Parking/searchResults"

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en-IN;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    "cache-control": "max-age=0",
    "connection": "keep-alive",
    "content-type": "application/x-www-form-urlencoded",
    "dnt": "1",
    "host": "a836-citypay.nyc.gov",
    "origin": "https://a836-citypay.nyc.gov",
    "referer": "https://a836-citypay.nyc.gov/citypay/Parking?stage=procurement",
    "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
}

cookies = {
    "PLAY_SESSION": "344892191ca51029cce3cd1051b6edf0be90e4ee-sessionId=0591b429-bf6d-4729-88e8-e4a08bd7982b",
    "_ga": "GA1.1.936749870.1751547363",
    "ak_bmsc": "65F69B1BBC3AA6212ED13B875BA788BE~000000000000000000000000000000~YAAQdOgyF3zOyqqXAQAAt/UW0RyJpTR+DOjuCkpOw/2nSO4PikqVPqs2rxsd8fIZxTHr9Wh14P1xaqZhzNaQ6PjC+o03b0YBJHSWyoRw4sZx9/Ba7tD6sx1rzSZFY6RwWOHmtMlGUTzllw/2clN8jrP69i9uNgryMRRnQ2Z1LM5KBBNnAmakgiGKeJniITxC9MlrKdg/8eS0LgrKlTbUc0QgAMiuzLGeylWrd6TwrY1ditNCWjWWREm8Z3rZlvDQXN0USpYLg6YyEBskLPHJAiasY+vWhIKX58hMVE4/eJwFLYpF6MWYqB1hzVCosQn4S+5Tj0bOlRBmd49u7IvdfBYL2NUZ68G4pOcxcbUfkMiJjZHLbJhuyxfardU=",
    "bm_sv": "26B15900EE257BFEDC1F58AAF23C638F~YAAQdOgyF4nOyqqXAQAA8PkW0RxKvvKPPs7Uhww82+dY851vTlzV85DQ0JMTHcR+gFjJNjdj/GJmVM7Mo7qxOcrGu+Sie1uTRnRc1G6J6cw9ukn8Ps6GyDK/Z6yswx+0XN3Ub+1FHv2asjlzZnaH7hnpefio1bjJNLokBYBh0VlfgtDHZ8c5fGEuWybOl/Wq5S4L/TRHb84zvfBMnUK6hDio2irGsgxSWE2GuastS3Q1UYZ5D4ssdRkfDzNs~1",
    "RT": 'z=1&dm=nyc.gov&si=bh41lnpuw6o&ss=mcnldr5z&sl=1&tt=0&obo=1&ld=vb&r=f5f9995d8ea0dc79e64e2fca037647c1&ul=ve&hd=vl',
    "_ga_QDJPRHTWJF": "GS2.1.s1751558351$o2$g1$t1751560880$j60$l0$h0"
}

data = {
    "VIOLATION_NUMBER": "9164311661",
    "g-recaptcha-response": "knlaskndlkasndlnsaloinaoidnslknaslkdnaslkdnaslkdnalskdnaslkdnaslkdnaslkdnaslkdnaslkdnaslkdnaslkdnaslkdnaslkdnasl",
}

response = requests.post(url, headers=headers, cookies=cookies, data=data)
print(response.status_code)
with open('response.html', 'w', encoding='utf-8') as f:
    f.write(response.text)
print("Response saved to response.html")