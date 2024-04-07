from typing import List

import pymongo
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from llama_index.core.settings import Settings
from llama_index.legacy.vector_stores import MongoDBAtlasVectorSearch

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from app.config.settings import settings

from llama_index.core import Document
from llama_index.core.schema import MetadataMode
from llama_index.core.node_parser import SentenceSplitter


DB_NAME = "company_knowlegde"
EMBEDDING_DIMENSION = 256
EMBEDDING_MODEL = "text-embedding-3-small"
MONGODB_URI = (
    f"mongodb+srv://brandypiao2021:{settings.MONGODB_PASSWORD}@hackthathon.zztaqau.mongodb.net/?"
    f"retryWrites=true&w=majority&appName=hackthathon"
)


embed_model = OpenAIEmbedding(
    model=EMBEDDING_MODEL, api_key=settings.OPEN_AI_KEY, dimensions=EMBEDDING_DIMENSION
)
llm = OpenAI(api_key=settings.OPEN_AI_KEY)
Settings.llm = llm
Settings.embed_model = embed_model


def get_base_url(url):
    # Extract scheme and netloc
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def check_url(url_initial, url):
    # Parse the initial URL and the URL to be checked
    parsed_initial = urlparse(url_initial)
    parsed_url = urlparse(url)

    # Extract the domain names, ignoring possible 'www.' prefixes
    domain_initial = parsed_initial.netloc.split("www.")[-1]
    domain_url = parsed_url.netloc.split("www.")[-1]

    # Check if the domain names match and if the URL to be checked starts with the base URL
    return domain_url == domain_initial and url.startswith(
        parsed_initial.scheme + "://"
    )


def scrape_website(url_initial):
    urls_to_scrap, urls_scraped = [url_initial], []
    i = 0
    scraped_dict = {}

    while len(urls_to_scrap) != 0 and i <= 50:
        url = urls_to_scrap[0]
        if not check_url(url_initial, url) or url in urls_scraped:
            urls_to_scrap.pop(0)
            continue

        else:
            urls_scraped.append(url)
            urls_to_scrap.pop(0)
            data = []

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }

            response = requests.get(url, headers=headers)

            if response.status_code == 200:
                html = response.text

                # Parse the HTML content
                soup = BeautifulSoup(html, "html.parser")

                # Extracting all hyperlinks
                for link in soup.find_all("a"):
                    href = link.get("href")
                    if type(href) == str:
                        if href not in urls_scraped and href not in urls_to_scrap:
                            urls_to_scrap.append(href)

                page_title = soup.title.text if soup.title else "No title found"

                # Extracting all text from paragraphs
                paragraphs = soup.find_all("p")
                for paragraph in paragraphs:
                    data.append(paragraph.text.strip())

                scraped_dict[page_title] = data
            i += 1

    return scraped_dict


def generate_dict_web_page(list_urls):
    dict = {}
    for url in list_urls:
        square_website = scrape_website(url)
        joined_dict_website = {
            key: "---".join(val) for key, val in square_website.items()
        }
        dict = dict | joined_dict_website
    return dict


def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB."""
    try:
        client = pymongo.MongoClient(mongo_uri)
        print("Connection to MongoDB successful")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None


def scrape_and_index_website(urls: List[str], company_name: str) -> None:
    # Scraping
    web_pages = generate_dict_web_page(urls)

    # Create document embedding
    llama_documents = []
    for page in web_pages:
        # Create a Document object with the text and excluded metadata for llm and embedding models
        llama_document = Document(
            text=web_pages[page],
            metadata={"page_title": page},
            excluded_llm_metadata_keys=[""],
            excluded_embed_metadata_keys=[""],
            metadata_template="{key}=>{value}",
            text_template="Metadata: {metadata_str}\n-----\nContent: {content}",
        )
        llama_documents.append(llama_document)

    parser = SentenceSplitter()
    nodes = parser.get_nodes_from_documents(llama_documents)
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode=MetadataMode.ALL)
        )
        node.embedding = node_embedding

    mongo_client = get_mongo_client(MONGODB_URI)
    db = mongo_client[DB_NAME]
    collection = db[company_name]

    # To ensure we are working with a fresh collection
    # delete any existing records in the collection
    collection.delete_many({})

    vector_store = MongoDBAtlasVectorSearch(
        mongo_client,
        db_name=DB_NAME,
        collection_name=company_name,
        index_name="vector_index",
    )
    vector_store.add(nodes)


if __name__ == "__main__":
    scrape_and_index_website(company_name="mongodb", urls=["https://www.mongodb.com/"])
