# undust.py
[![Python](https://img.shields.io/badge/Python-%E2%89%A5%203.12-yellow.svg)](https://www.python.org/) 
<img src="https://img.shields.io/badge/Developed%20on-kali%20linux-blueviolet">
[![License](https://img.shields.io/badge/License-BSD-red.svg)](https://github.com/t3l3machus/undust.py/blob/main/LICENSE)
<img src="https://img.shields.io/badge/Maintained%3F-Yes-96c40f">

`Undust` is a URL pattern generator that helps uncover archived, backup, and temporary files left behind on web servers. Given a URL, it generates the most common file variants like 'gz', 'rar', 'tar', 'zip', 'swp', 'swo', 'swn', 'bak', 'bak1', 'bak2', 'backup', 'old', 'copy', 'save', 'txt', 'tmp', 'temp', and more. With the `-a` option, it recursively generates these patterns across all parent directories in the path to maximize coverage.
![image](https://github.com/user-attachments/assets/291143de-76a2-455b-ba2e-4080a7c87a58)



## Installation
No special requirements:
```
git clone https://github.com/t3l3machus/undust.py
```
## Usage examples
Undust requires URLs as input to generate archive and backup filename variations. It works great in combination with tools like `katana` and `httpx` by [ProjectDiscovery](https://github.com/projectdiscovery).  
Crawl a target app for urls, pipe them to undust and then to httpx for discovery:
```
katana -u https://example.com -jc -d 3 -silent -ef js,css,png,jpg,ico,json | python3 undust.py -s -q -a | httpx -sc -cl -title -timeout 2 -mc 200 -silent
```
❗Keep in mind that, this command matches only 200 status responses. You will see no output if no archive is found, which is a rare occasion anyway.

## Options
```
usage: undust.py [-h] [-f FILE] [-s] [-sq] [-eo] [-l LENGTH] [-a] [-q]

options:
  -h, --help            show this help message and exit

BASIC OPTIONS:
  -f FILE, --file FILE  File containing urls to process.
  -s, --stream          Read input from stdin as a stream.
  -sq, --strip-query    Strip URL query strings from the input.
  -eo, --extension-only
                        Ignore endpoints that have no file extension.
  -l LENGTH, --length LENGTH
                        Limit the maximum acceptable url length, usefull for skipping very long urls (default: None, recommended: between 400 - 600).
  -a, --all-dirs        When enabled, this option walks back through each parent directory of the given URL and generates archive and backup filename patterns at each level.
  -q, --quiet           Do not print the banner on startup.
```
