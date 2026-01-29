"""
Web scraper for E2M Solutions website
Extracts content from pages and prepares it for vector storage
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

class E2MScraper:
    def __init__(self, base_url="https://www.e2msolutions.com/"):
        self.base_url = base_url
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url):
        """Scrape a single page and return cleaned content"""
        try:
            if url in self.visited_urls:
                return None
            
            print(f"Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.visited_urls.add(url)
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            
            # Get page title
            title = soup.title.string if soup.title else url
            
            # Get meta description
            meta_desc = ""
            meta_tag = soup.find('meta', attrs={'name': 'description'})
            if meta_tag and meta_tag.get('content'):
                meta_desc = meta_tag['content']
            
            return {
                'url': url,
                'title': title,
                'description': meta_desc,
                'content': cleaned_text,
                'chunks': self._chunk_text(cleaned_text, title)
            }
            
        except Exception as e:
            print(f"Error scraping {url}: {str(e)}")
            return None
    
    def _chunk_text(self, text, title, chunk_size=500):
        """Split text into chunks for better embedding"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append({
                'text': chunk,
                'title': title,
                'position': i // chunk_size
            })
        
        return chunks
    
    def scrape_website(self, max_pages=10):
        """Scrape multiple pages from the website"""
        pages_to_scrape = [
            self.base_url,
            urljoin(self.base_url, "/services"),
            urljoin(self.base_url, "/white-label"),
            urljoin(self.base_url, "/hire-remote-team"),
            urljoin(self.base_url, "/work"),
            urljoin(self.base_url, "/company"),
            urljoin(self.base_url, "/contact-us"),
        ]
        
        scraped_data = []
        
        for url in pages_to_scrape[:max_pages]:
            data = self.scrape_page(url)
            if data:
                scraped_data.append(data)
                time.sleep(1)  # Be respectful with scraping
        
        return scraped_data
    
    def get_page_links(self, url):
        """Extract all links from a page"""
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = []
            for link in soup.find_all('a', href=True):
                full_url = urljoin(url, link['href'])
                
                # Only include links from the same domain
                if urlparse(full_url).netloc == urlparse(self.base_url).netloc:
                    links.append(full_url)
            
            return list(set(links))
        except Exception as e:
            print(f"Error getting links from {url}: {str(e)}")
            return []
