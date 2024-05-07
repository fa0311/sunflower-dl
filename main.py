import concurrent.futures
import os
import re
import subprocess
import urllib.parse
import urllib.request

urls = [
    "http://172.16.0.1/sp/cinema.html",
    "http://172.16.0.1/sp/cinema2.html",
    "http://172.16.0.1/sp/cinema3.html",
]

detail_base_url = "http://172.16.0.1/sp/cinema_detail.html?id={id}"

output = "output"
os.makedirs(output, exist_ok=True)

pattern1 = re.compile(
    r'<a class="slide" href="(.*?)"><img src="(.*?)" alt="(.*?)" /><span>(.*?)</span></a>'
)
pattern2 = re.compile(
    r'<a href="(.*?)" class="detailbtn">再生する<br /><span>Play</span></a>'
)


commands = []
for url in urls:
    with urllib.request.urlopen(url) as response:
        html = response.read().decode("utf-8")
        row = pattern1.findall(html)
        for data in row:
            query: urllib.parse.ParseResult = urllib.parse.urlparse(data[0])
            id = urllib.parse.parse_qs(query.query)["id"][0]
            detail_url = detail_base_url.format(id=id)
            with urllib.request.urlopen(detail_url) as response:
                detail_html = response.read().decode("utf-8")
                detail = pattern2.findall(detail_html)
                title = data[2] if data[2] != "" else id
                command = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    detail[0],
                    "-c",
                    "copy",
                    f"{output}/{title}.mp4",
                ]
                commands.append(command)


print(commands)


with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    executor.map(subprocess.run, commands)
