from imports import *
from scraper import WebScraper

if __name__ == "__main__": #marcador de posición
    scraper = WebScraper("https://tambinsoyunal.fandom.com/es/wiki/Universidad_Nacional_de_Colombia")
    titulos = scraper.extract_titles()
    parrafos = scraper.extract_paragraphs()

    print("=== TÍTULOS ===")
    for t in titulos:
        print("-", t)

    print("\n=== PÁRRAFOS (primeros 5) ===")
    for p in parrafos[:5]:
        print(p, "\n")
