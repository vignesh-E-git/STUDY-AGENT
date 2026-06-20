from firecrawl import Firecrawl
from firecrawl import FirecrawlApp
from firecrawl.v2.types import ScrapeOptions # for v2 firecrawl
from dotenv import load_dotenv

load_dotenv()

firecrawler = FirecrawlApp()

#----------------------------------------
def clean_search(results):
    clean = ""
    items = []

    # Firecrawl v2 search returns a SearchData object with fields web/news/images.
    if hasattr(results, "web") or hasattr(results, "news") or hasattr(results, "images"):
        if getattr(results, "web", None):
            items.extend(results.web)
        if getattr(results, "news", None):
            items.extend(results.news)
        if getattr(results, "images", None):
            items.extend(results.images)
    else:
        items = list(results)

    for res in items:
        clean += f"TITLE: {getattr(res, 'title', '')}\n"
        clean += f"URL: {getattr(res, 'url', '')}\n"
        clean += f"DESCRIPTION: {getattr(res, 'description', '')}\n"
        clean += "-" * 50 + "\n"
    return clean

#------------------------------------------
def clean_scrape(results):
    return results.markdown[:50] or ""
#-----------------------------------------

def search_website(query:str)->str:
    print(f"SEARCHING WEBSITE FOR THE QUERY : {query}")
    try:
        result = firecrawler.search(
            query=f'{query} , best websites',
            limit=3,
            scrape_options= ScrapeOptions(formats=["markdown"])
            )
        return clean_search(result)
    except Exception as e:
        print("FAILED TO SEARCH THE WEBSITE.")
        print(f'ERROR : {e}')
        return ''
    
#----------------------------------------------
def scrape_website(url:str)->str:
    print("SCRAPING WEBSITE ...")
    try:
        result = firecrawler.scrape(
            url,
            formats=["markdown"]
        )
        return clean_scrape(result)
    except Exception as e:
        print("FAILED TO SCRAP WEBSITE.")
        print(f"ERROR : {e}")
        return ''
    
#-------------------------------------------  
#  
# search_website("which is best for buying phones?")
# print(scrape_website('https://www.apple.com'))