#!/usr/bin/env python3
# Author: Panagiotis Chartas (t3l3machus)

import sys, argparse
from urllib.parse import urlparse
from time import sleep

''' Colors '''
ORANGE = '\033[0;38;5;214m'
FAIL = '\033[1;91m'
GRAY = '\033[38;5;246m'
RST = '\033[0m'

''' Prefixes '''
DEBUG = f'[{ORANGE}Debug{RST}]'
ERROR = f'[{FAIL}Error{RST}]'
SKIPPED = f'[{GRAY}Skipped{RST}]'


# -------------- Arguments -------------- #
parser = argparse.ArgumentParser(
    description=""
)
basic_group = parser.add_argument_group('BASIC OPTIONS')
basic_group.add_argument("-f", "--file", action="store", help = "File containing urls to process.")
basic_group.add_argument("-s", "--stream", action="store_true", help = "Read input from stdin as a stream.")
basic_group.add_argument("-sq", "--strip-query", action="store_true", help = "Strip URL query strings from the input.")
basic_group.add_argument("-eo", "--extension-only", action="store_true", help = "Ignore endpoints that have no file extension.")
basic_group.add_argument("-l", "--length", action="store", type = int, help = "Limit the maximum acceptable url length, usefull for skipping very long urls (default: None, recommended: between 400 - 600). ")
basic_group.add_argument("-a", "--all-dirs", action="store_true", help = "When enabled, this option walks back through each parent directory of the given URL and generates archive and backup filename patterns at each level.")
basic_group.add_argument("-q", "--quiet", action="store_true", help = "Do not print the banner on startup.")

args = parser.parse_args()


def do_nothing():
    pass


def print_debug(txt):
    print(f'{DEBUG} {txt}')


def exit_with_msg(txt):
    print_debug(txt)
    exit(1)



class Global:
    archive_extensions = set(['gz', 'rar', 'tar', 'zip', 'swp', 'swo', 'swn', 'bak', 'bak1', 'bak2', 'backup', 'old', 'copy', 'save', 'txt', 'tmp', 'temp', '~', '1', '2'])
    archive_symbols = set(['.', '_', '__', '~', '._'])
    archive_patterns = set(['_VAL_', '__VAL__', '--VAL--', 'VAL--old', '__VAL_backup__', '__VAL__.bak'])



def split_url(url):
    parsed = urlparse(url)
    base_url_raw = f"{parsed.scheme}://{parsed.netloc}/"
    path_parts = parsed.path.strip('/').split('/')
    directories = []

    path_parts = [p for p in path_parts if p]

    if parsed.path.endswith('/') or not path_parts:
        last_segment = False
        base_path_parts = path_parts
    else:
        last_segment = path_parts[-1]
        base_path_parts = path_parts[:-1]

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    if base_path_parts:
        base_url += '/' + '/'.join(base_path_parts)

    query = parsed.query if parsed.query else False
    directories += base_path_parts  

    return [base_url_raw, base_url + '/', last_segment, query, directories]



def get_file_contents(file_path):
    try:
        f = open(file_path, 'r', encoding="utf-8", errors="ignore")
        contents = f.read().split('\n')
        contents = [l.strip() for l in contents if l.strip()]
        f.close()
        return contents
    except:
        exit_with_msg(f'Failed to read file {args.file}.')
        return False



def is_valid_url(url):
    try:
        parsed = urlparse(url)
        return all([parsed.scheme in ['http', 'https'], parsed.netloc])
    except Exception:
        return False



def generate_archive_urls(base_url, endpoint, query, ext):
    for val in Global.archive_extensions:
        print(f'{base_url}{endpoint}.{val}{query}')
        print(f'{base_url}{endpoint}.{ext}.{val}{query}') if ext else do_nothing()

    for s in Global.archive_symbols:
        print(f'{base_url}{s}{endpoint}{query}')
        print(f'{base_url}{s}{endpoint}.{ext}{query}') if ext else do_nothing()

    for p in Global.archive_patterns:
        print(f"{base_url}{p.replace('VAL', endpoint)}{query}")
        print(f"{base_url}{p.replace('VAL', f'{endpoint}.{ext}')}{query}") if ext else do_nothing()



def undust(url):

    try:
        if args.length:
            if len(url) > args.length:
                return
            
        if not is_valid_url(url):
            print(f"{SKIPPED} {GRAY}{url} (not a valid http url){RST}", file=sys.stderr)
            return
        
        base_url_raw, base_url, endpoint, query, directories = split_url(url)


        if not endpoint:
            print(f"{SKIPPED} {GRAY}{url} (no endpoint to mutate){RST}", file=sys.stderr)
            return
        
        endpoint = endpoint.strip()
        ext = ''

        if endpoint.count('.'):
            tmp = endpoint.rsplit('.', 1)
            endpoint = tmp[0]
            ext = tmp[1]

        if args.extension_only and not ext:
           print(f"{SKIPPED} {GRAY}{url} (extentions-only enabled){RST}", file=sys.stderr)
           return
        
        query = '' if not query or args.strip_query else f'?{query}'
        
        if not args.all_dirs or not directories:
            generate_archive_urls(base_url, endpoint, query, ext)

        else:
            path = ''
            generate_archive_urls(f'{base_url_raw}', endpoint, query, ext)

            for dir in directories:
                path += dir + '/'
                generate_archive_urls(f'{base_url_raw}{path}', endpoint, query, ext)

    except Exception as e:
        print(f'{ERROR} Something went wrong with {url}: {e}', file=sys.stderr)
        exit()



def print_banner():
    print()
    banner_lines = [
        "              |          |    ",
        ".   .,---.,---|.   .,---.|--- ",    
        "|   ||   ||   ||   |`---.|    ",   
        "`---'`   '`---'`---'`---'`---'"   
    ]
    
    def rgb_escape(r, g, b):
        return f"\033[38;2;{r};{g};{b}m"

    base_r, base_g, base_b = 255, 255, 255
    step = 30  

    for i, line in enumerate(banner_lines):
        r = max(0, base_r - step * i)
        g = max(0, base_g - step * i)
        b = max(0, base_b - step * i)
        print(f"  {rgb_escape(r, g, b)}{line}{RST}")
    print()   



def main():
    
    print_banner() if not args.quiet else do_nothing()
    
    if args.stream and args.file:
        exit_with_msg('Cannot use both --stream and --file. Select only one.')
    elif not args.stream and not args.file:
        exit_with_msg('No input provided. You must use --stream or --file.')

    if args.stream:
        for url in sys.stdin:
            url = url.strip()

            if not url:
                sleep(0.1)
                continue

            undust(url)  

    elif args.file:
        urls = get_file_contents(args.file)
        for url in urls:
            undust(url)


if __name__ == '__main__':
    main()
