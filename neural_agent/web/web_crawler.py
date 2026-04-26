import requests
from bs4 import BeautifulSoup
import urllib.parse
import re

class WebCrawler:
    def __init__(self, agent):
        self.agent = agent
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (NeuralAgent/1.0)"
        })
        self.visited = set()

    def fetch(self, url, timeout=30):
        try:
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"Error fetching {url}: {e}"

    def parse(self, html):
        soup = BeautifulSoup(html, "html.parser")
        
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, "html.parser")
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urllib.parse.urljoin(base_url, href)
            links.append(full_url)
        return links

    def crawl(self, url, depth=1, max_pages=10):
        if depth > max_pages:
            return []
        
        if url in self.visited:
            return []
        
        self.visited.add(url)
        
        html = self.fetch(url)
        if html.startswith("Error"):
            return [{"url": url, "content": html}]
        
        content = self.parse(html)
        
        results = [{"url": url, "content": content[:5000]}]
        
        if depth < max_pages:
            links = self.extract_links(html, url)[:5]
            for link in links:
                results.extend(self.crawl(link, depth + 1, max_pages))
        
        return results

    def search(self, query, limit=10):
        url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
        html = self.fetch(url)
        
        soup = BeautifulSoup(html, "html.parser")
        results = []
        
        for div in soup.find_all("div", class_="g")[:limit]:
            title_elem = div.find("h3")
            link_elem = div.find("a")
            if title_elem and link_elem:
                results.append({
                    "title": title_elem.get_text(),
                    "url": link_elem.get("href", "")
                })
        
        return results

    def summarize_page(self, url):
        html = self.fetch(url)
        if html.startswith("Error"):
            return html
        
        soup = BeautifulSoup(html, "html.parser")
        
        title = soup.title.string if soup.title else "No title"
        
        meta_desc = soup.find("meta", {"name": "description"})
        description = meta_desc.get("content", "") if meta_desc else ""
        
        return {
            "title": title,
            "description": description,
            "content": self.parse(html)[:2000]
        }