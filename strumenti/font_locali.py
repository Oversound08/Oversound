"""Font sul sito senza passare da Google (privacy): scarica Archivo e Inter da Google Fonts una volta,
li salva in /font/ e fa usare al sito /font/font.css. Gira su GitHub (Actions), che può raggiungere Google."""
import os, re, urllib.request

URL = "https://fonts.googleapis.com/css2?family=Archivo:wght@600;700;800;900&family=Inter:wght@400;500;600;700&display=swap"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
VECCHIO = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="' + URL.replace("&", "&amp;") + '">', '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
           '<link rel="stylesheet" href="' + URL + '">')
NUOVO = '<link rel="preload" href="/font/font.css" as="style"><link rel="stylesheet" href="/font/font.css">'
RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scarica(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=60).read()


def main():
    css = scarica(URL).decode("utf-8"); cart = os.path.join(RADICE, "font"); os.makedirs(cart, exist_ok=True); nomi = {}
    blocchi = re.findall(r"/\*\s*([\w-]+)\s*\*/\s*(@font-face\s*\{[^}]*\})", css)
    out = []
    for subset, b in blocchi:
        fam = re.search(r"font-family:\s*'([^']+)'", b).group(1).lower().replace(" ", "-")
        w = re.search(r"font-weight:\s*([\d ]+);", b).group(1).strip().replace(" ", "-")
        u = re.search(r"url\((https://[^)]+)\)", b).group(1)
        if u not in nomi:
            nomi[u] = f"{fam}-{subset}-{w}.woff2"
            with open(os.path.join(cart, nomi[u]), "wb") as fh: fh.write(scarica(u))
        out.append(f"/* {subset} */\n" + b.replace(u, "/font/" + nomi[u]))
    assert out, "nessun font trovato"
    with open(os.path.join(cart, "font.css"), "w", encoding="utf-8") as fh: fh.write("/* Archivo e Inter (SIL Open Font License) serviti da oversound.it */\n" + "\n".join(out) + "\n")
    print(len(nomi), "file di font salvati")
    p = os.path.join(RADICE, "index.html"); s = open(p, encoding="utf-8").read()
    for v in VECCHIO:
        if v in s: s = s.replace(v, NUOVO); open(p, "w", encoding="utf-8").write(s); print("index.html: font da oversound.it"); break


if __name__ == "__main__":
    main()
