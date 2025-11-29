from imports import *
from driver import get_driver

class WebScraper:
    def __init__(self, url, use_selenium=False):
        self._url = url
        self.use_selenium = use_selenium
        self.driver = get_driver() if use_selenium else None
        self._html = None
        self._soup = None

    def get_url(self):
        return self._url

    def set_url(self, nueva_url):
        if not nueva_url.startswith("http"):
            raise ValueError("La URL no es válida.")
        self._url = nueva_url

    def _fetch_html(self, url=None):
        if url is None:
            url = self._url
        response = requests.get(url)
        if response.status_code == 200:
            self._html = response.text
        else:
            raise Exception(f"Error al acceder a {url} ({response.status_code})")

    def _parse_html(self):
        if not self._html:
            raise Exception("No se ha descargado el HTML todavía.")
        self._soup = BeautifulSoup(self._html, "html.parser")
        return self._soup

    def extract_titles(self):
        self._fetch_html()
        soup = self._parse_html()
        titulos = soup.find_all("h2")
        return [t.get_text(strip=True) for t in titulos]
    
    def extract_paragraphs(self):
        self._fetch_html()
        soup = self._parse_html()
        contenedor = soup.find("div", class_="mw-parser-output")
        if not contenedor:
            return []
        parrafos = [p.get_text(strip=True) for p in contenedor.find_all("p")]
        return parrafos

class NewsParser:
    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")

        return {
            "title": soup.find("h1").get_text(strip=True) if soup.find("h1") else "Sin título",
            "lead": soup.find("p").get_text(strip=True) if soup.find("p") else "",
            "author": "Desconocido",
            "date": datetime.now(),
            "section": "General",
            "tags": [tag.get_text(strip=True) for tag in soup.find_all("a", class_="tag")],
            "url": "",  # podrías pasarla desde fuera si quieres
            "text": " ".join(p.get_text(strip=True) for p in soup.find_all("p")),
            "scrape_date": datetime.now()
        }

class ProgramParser:
    def parse(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        data = {
            "program_name": soup.find("h1", class_="program-title").get_text(strip=True) if soup.find("h1", class_="program-title") else "",
            "level": soup.find("span", class_="level").get_text(strip=True) if soup.find("span", class_="level") else "",
            "sede": soup.find("span", class_="sede").get_text(strip=True) if soup.find("span", class_="sede") else "",
            "faculty": soup.find("span", class_="faculty").get_text(strip=True) if soup.find("span", class_="faculty") else "",
            "snies": soup.find("span", class_="snies").get_text(strip=True) if soup.find("span", class_="snies") else "",
            "modalidad": soup.find("span", class_="modalidad").get_text(strip=True) if soup.find("span", class_="modalidad") else "",
            "url": soup.find("a", class_="program-link")["href"] if soup.find("a", class_="program-link") else "",
            "scrape_date": datetime.now()
        }

        return data

class EventParser:
    def parse(self, html: str) -> dict:
        soup = BeautifulSoup(html, "html.parser")

        data = {
            "title": soup.find("h1", class_="event-title").get_text(strip=True) if soup.find("h1", class_="event-title") else "",
            "date_start": self._parse_date(soup.find("span", class_="date-start").get_text(strip=True)) if soup.find("span", class_="date-start") else date.today(),
            "date_end": self._parse_date(soup.find("span", class_="date-end").get_text(strip=True)) if soup.find("span", class_="date-end") else date.today(),
            "location": soup.find("span", class_="location").get_text(strip=True) if soup.find("span", class_="location") else "",
            "organizer": soup.find("span", class_="organizer").get_text(strip=True) if soup.find("span", class_="organizer") else "",
            "registration_url": soup.find("a", class_="registration")["href"] if soup.find("a", class_="registration") else "",
            "description": soup.find("div", class_="description").get_text(strip=True) if soup.find("div", class_="description") else "",
            "scrape_date": datetime.now()
        }

        return data

    def _parse_date(self, date_str: str) -> date:
        """Convierte una cadena de texto en un objeto date."""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # Si el formato cambia (ej: '10 de noviembre de 2025'), se puede ajustar aquí
            return date.today()
        
class WikiScraper:
    def scrape(self, topic):
        url = f"https://es.wikipedia.org/wiki/{topic.replace(' ', '_')}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            parrafos = [p.get_text(strip=True) for p in soup.find_all("p")]
            return parrafos[:3]
        else:
            return []

class UniversityScraper(WebScraper):
    def __init__(self, base_url):
        super().__init__(base_url)
        self.news_parser = NewsParser()
        self.program_parser = ProgramParser()
        self.event_parser = EventParser()
        self.wiki_scraper = WikiScraper()

    def scrape_news(self):
        self._fetch_html(self._url + "/noticias")
        soup = self._parse_html()
        return self.news_parser.parse(str(soup))

    def scrape_programs(self):
        self._fetch_html(self._url + "/programas")
        soup = self._parse_html()
        return self.program_parser.parse(str(soup))

    def scrape_events(self):
        self._fetch_html(self._url + "/eventos")
        soup = self._parse_html()
        return self.event_parser.parse(str(soup))

    def scrape_wikipedia(self, topic):
        return self.wiki_scraper.scrape(topic)
    
class Article:
    def __init__(self, parser: NewsParser, html: str):
        self.parser = parser
        data = parser.parse(html)  # ahora sí le pasamos el HTML

        self.title: str = data.get("title", "")
        self.lead: str = data.get("lead", "")
        self.author: str = data.get("author", "")
        self.date: datetime = data.get("date", datetime.now())
        self.section: str = data.get("section", "")
        self.tags: List[str] = data.get("tags", [])
        self.url: str = data.get("url", "")
        self.text: str = data.get("text", "")
        self.scrape_date: datetime = data.get("scrape_date", datetime.now())

    def __str__(self):
        return f"{self.title} - {self.author} ({self.section})"
    
class Program:
    def __init__(self, parser: 'ProgramParser', html: str):
        self.parser = parser
        data = parser.parse(html)  # el parser extrae los datos del HTML

        self.program_name: str = data.get("program_name", "")
        self.level: str = data.get("level", "")
        self.sede: str = data.get("sede", "")
        self.faculty: str = data.get("faculty", "")
        self.snies: str = data.get("snies", "")
        self.modalidad: str = data.get("modalidad", "")
        self.url: str = data.get("url", "")
        self.scrape_date: datetime = data.get("scrape_date", datetime.now())

class Event:
    def __init__(self, parser: 'EventParser', html: str):
        self.parser = parser
        data = parser.parse(html)  # el parser extrae la info del HTML

        self.title: str = data.get("title", "")
        self.date_start: date = data.get("date_start", date.today())
        self.date_end: date = data.get("date_end", date.today())
        self.location: str = data.get("location", "")
        self.organizer: str = data.get("organizer", "")
        self.registration_url: str = data.get("registration_url", "")
        self.description: str = data.get("description", "")
        self.scrape_date: datetime = data.get("scrape_date", datetime.now())







