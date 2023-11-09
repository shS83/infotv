import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlsplit

all_tables = []
comics = []


def scrape(url: str):
    domain = urlsplit(url).netloc
    to_return = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    status = response.status_code
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    print(f'Scraping: {soup.title.get_text()}')
    print("Site status OK" if status == 200 else f"ERROR {status}")

    if 'yle' in domain:
        scraped = soup.find_all("a", class_=re.compile("MinimalHeadlines__Link"))
        for s in scraped:
            to_return.append({'title': s.get_text(), 'href': s['href']})

    elif 'iltalehti' in domain:
        full = soup.find('div', class_='full-article')
        head_full = full.find_next('div', class_='front-title')
        fullhref = full.find_next('a')
        to_return.append({'title': head_full.get_text(), 'href': fullhref['href']})
        halves = soup.find_all("a", class_='half-article-content')

        for h in halves:
            halfhead = h.find_next('div', class_='front-title')
            to_return.append({'title': halfhead.get_text(), 'href': h['href']})

    elif 'pelaaja' in domain:
        scraped = soup.find_all("a", class_='block')
        for s in scraped:
            ugly = s.get_text().strip().split('\n')
            if 'image/svg+xml' in ugly[0] or 'Episodi.fi' in ugly[0]:
                continue
            prettier = ugly[0].replace('Uutinen | ', '')
            to_return.append({'title': prettier, 'href': s['href']})

    elif 'tomshardware' in domain:
        scraped = soup.find_all("a", class_='article-link')
        for s in scraped:
            ugly = s.get_text().strip().split('\n')
            to_return.append({'title': ugly[0], 'href': s['href']})

    elif 'mikrobitti' in domain:
        first = soup.find('div', id='skyscraper-height-div')
        scraped = first.find_all_next("a", href=re.compile("/uutiset/"))
        for s in scraped:
            title = s.find_next('span', class_='title')
            to_return.append({'title': title.get_text(), 'href': f'http://{domain}{s["href"]}'})
            # print(f'http://{domain}{s["href"]}', title.get_text())

    elif 'muropaketti' in domain:
        heads = soup.find_all("h3", class_=re.compile("box-item__headline"))
        # print(heads)

        for s in heads:
            item = s.find_next('a', href=re.compile("muropaketti"))
            # print(scraped)
            to_return.append({'title': item.get_text(), 'href': item['href']})

    else:
        return False

    domain_split = domain.split('.')

    if 'www' in domain_split:
        d_name = domain_split[1]
    else:
        d_name = domain_split[0]

    generated_table = generate_table_html(to_return, f'https://{domain}', d_name)

    return generated_table


def get_comic(url: str):
    domain = urlsplit(url).netloc
    comic = False
    response = requests.get(url)
    status = response.status_code
    content = response.content
    soup = BeautifulSoup(content, "html.parser")
    print(f'Scraping: {soup.title.get_text()}')
    print("Site status OK" if status == 200 else "ERROR")

    if 'hs' in url:
        scraped = soup.find("div", class_=re.compile("cartoon-content"))
        a = scraped.find_next('a')
        img = a.find_next('img')
        comic = f'http:{img["data-srcset"].split(" ")[0]}'

    if 'smbc' in url:
        scraped = soup.find("img", id=re.compile("cc-comic"))
        comic = scraped['src']

    if 'xkcd' in url:
        scraped = soup.find("div", id=re.compile("comic"))
        img = scraped.find_next('img')
        comic = f'http:{img["src"]}'

    if 'oglaf' in url:
        scraped = soup.find("img", id=re.compile("strip"))
        comic = scraped['src']

    domain_split = domain.split('.')

    if 'www' in domain_split:
        d_name = domain_split[1]
    else:
        d_name = domain_split[0]

    comic_table = comics_to_tables(comic, f'https://{domain}', d_name)

    return comic_table


def generate_table_html(scraped_list: list, url_prefix: str, domain: str):
    global all_tables

    c = 10
    b = 1
    table_html = [f'<table class="taulu" id="taulu{len(all_tables)}">',
                  f'<caption>{domain.upper()} Headlines</caption>']
    for item in scraped_list:
        gradient = f'background: linear-gradient(to bottom, rgb({b}, {b}, {b * 2}), rgb({c}, {c}, {c * 2}));'
        t_s = f'<tr><td style="{gradient}">'
        t_e = '</td></tr>'
        h_text = item['title'].replace('­', '')
        if domain in item['href']:
            address = item['href']
        else:
            address = f'{url_prefix}{item["href"]}'
        anchor = f'<a href="{address}">{h_text}</a>'
        table_html.append(f'{t_s}{anchor}{t_e}\n')
        b = c
        c += round(50 / len(scraped_list))

    table_html.append('</table>')
    return table_html


def comics_to_tables(comic: str, url_prefix: str, domain: str):
    global all_tables, comics
    title = domain.upper()
    if title == 'HS':
        title = 'FINGERPORI'

    table_html = [f'<table class="taulu" id="taulu{len(all_tables) + len(comics)}">',
                  f'<caption>{title}</caption>']
    t_s = '<tr><td>'
    t_e = '</td></tr>'
    anchor = f'<a href="{comic}"><img src="{comic}" alt="comic" /></a>'
    table_html.append(f'{t_s}{anchor}{t_e}\n')
    table_html.append('</table>')
    return table_html


def generate_page(tables_list: list):
    output_start = """<!DOCTYPE html>
    <html lang="fi">
    <head>
        <meta charset="UTF-8">
        <title>Headlines</title>
        <link rel="stylesheet" href="mock_style.css"/>
    </head>
    <body>
    """

    nav_start = '<nav class="navbar">\n'
    nav_end = '</nav>\n'

    output_start += nav_start

    for x, v in enumerate(tables_list):
        provider = v[1].split(' ')[0].replace('<caption>', '').lower()
        provider = provider[0].upper() + provider[1:]
        output_start += f'<button class="button after" type="button" onClick="change_{x}()">{provider}</button>\n'

    output_start += nav_end
    output_start += '<div id="container">\n'
    output_end = """
    </div>
    </body>
    </html>
    """

    print('Prettifying...')
    actual_output = output_start

    for table in tables_list:
        for row in table:
            actual_output += row

    # Add JS

    script_start = '<script type="text/javascript">'
    script_end = '</script>'

    actual_output += script_start

    for x, value in enumerate(tables_list):
        script_to_add = 'function change_' + str(x) + '() {\n'
        script_to_add += f'        let x = document.getElementById("taulu{x}");\n'
        script_to_add += '        if (x.style.display === "none") {\n'
        script_to_add += '            x.style.display = "";\n'
        script_to_add += '        } else {\n'
        script_to_add += '            x.style.display = "none";\n'
        script_to_add += '        }\n'
        script_to_add += '    }\n'
        actual_output += str(script_to_add)

    actual_output += script_end

    # End Add JS

    actual_output += output_end
    soppa = BeautifulSoup(actual_output, features="html.parser")
    prettier_soppa = soppa.prettify()

    print("Saving to file...")

    with open("FlaskTV/static/cache.html", "w", encoding="utf-8") as f:
        f.write(prettier_soppa)
    f.close()

    print("Done.")


def execute():
    global all_tables, comics

    urls = [
        "https://yle.fi/",
        'https://www.iltalehti.fi/uutiset',
        'https://www.pelaaja.fi/uutiset',
        'https://muropaketti.com/',
        'https://www.tomshardware.com/',
        'https://www.mikrobitti.fi/'
        ]

    for u in urls:
        all_tables.append(scrape(u))

    c_urls = [
        'https://www.hs.fi/fingerpori/',
        'https://www.smbc-comics.com/',
        'https://xkcd.com/',
        'https://www.oglaf.com/']

    for c_url in c_urls:
        comics.append(get_comic(c_url))

    all_tables.extend(comics)

    if False not in all_tables:
        generate_page(all_tables)


if __name__ == '__main__':
    execute()
