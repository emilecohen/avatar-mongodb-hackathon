import pymongo

from app.config.settings import settings


from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch

DB_NAME = "company_knowlegde"
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 256
embed_model = OpenAIEmbedding(
    model=EMBEDDING_MODEL, api_key=settings.OPEN_AI_KEY, dimensions=EMBEDDING_DIMENSION
)

# class CustomLLM:
#     def __init__(self, api_key):
#         self.llm = OpenAI(api_key=api_key)
#         self.metadata = {"name": "OpenAI", "version": "custom"}
#
#     def _call(self, prompt, **kwargs):
#         return self.llm.complete(prompt, **kwargs)
#
# llm = CustomLLM(api_key=settings.OPEN_AI_KEY)
# Settings.llm = llm
# Settings.embed_model = embed_model


llm = OpenAI(api_key=settings.OPEN_AI_KEY)
Settings.llm = llm
Settings.embed_model = embed_model


MONGODB_URI = (
    f"mongodb+srv://brandypiao2021:{settings.MONGODB_PASSWORD}@hackthathon.zztaqau.mongodb.net/?"
    f"retryWrites=true&w=majority&appName=hackthathon"
)

qa_prompt_tmpl_str = """
Context information is below.\n---------------------\n{context_str}\n---------------------\n
Act as a helpful salesman. Your role is to engage with potential clients, providing \
them with clear, accurate, and concise information about the company's products or services.
Your responses must be engaging, informative yet succinct, adhering to a strict word limit\
of 45 words per response. You will based all your answers on the following context:
Query: {query_str}
Answer : \
"""

# Ask question
qa_prompt_tmpl_str_v2 = """
Context information is below.\n---------------------\n{context_str}\n---------------------\n
Act as a helpful salesman. Your role is to engage with potential clients, providing \
them with clear, accurate, and concise information about the company's products or services.
Your responses must be engaging, informative yet succinct, adhering to a strict word limit\
of 45 words per response. If needed, ask a question back to the customer to help us understand their needs better. \
You will based all your answers on the following context:
Query: {query_str}
Answer : \
"""

# Ask question to understand customer's willingness to pay
qa_prompt_tmpl_str_v3 = """
Context information is below.\n---------------------\n{context_str}\n---------------------\n
Act as a helpful salesman. Your role is to engage with potential clients, providing \
them with clear, accurate, and concise information about the company's products or services.
Your responses must be engaging, informative yet succinct, adhering to a strict word limit\
of 45 words per response. When appropriate, ask a question back to the customer to help us understand their revenue and willingness to buy. \
You will based all your answers on the following context:
Query: {query_str}
Answer : \
"""

# Ask question based on conversation
qa_prompt_tmpl_str_v4 = """
Context information is below.\n---------------------\n{context_str}\n---------------------\n
Act as a helpful salesman. Your role is to engage with potential clients, providing \
them with clear, accurate, and concise information about the company's products or services.
Your responses must be engaging, informative yet succinct. Early in the conversation, ask questions \
to understand customer’s pain points and understand whether our products can address their business needs. \
If our products can address their needs, recommend them with appropriate products. \
Try to ask questions to understand customer’s business size and revenue, to help us understand \
their willingness to pay. If you think the customer is likely to pay for the product, try to connect\
 them with a sales representative and ask for their contact email.
Query: {query_str}
Answer : \
"""

system_prompt = """Act as a helpful salesman. Your role is to engage with potential clients, providing \
them with clear, accurate, and concise information about the company's products or services.
Your responses must be engaging, informative yet succinct adhering to a strict word limit\
of 45 words per response. Try to ask questions to understand customer’s business size and revenue, to help us understand \
If our products can address their needs, recommend them with appropriate products. Don't ask 2 questions in a row, try to find the right information, and report the \
right information with precision from the website and give an answer to the customer. \
their willingness to pay.
"""


def get_mongo_client(mongo_uri):
    """Establish connection to the MongoDB."""
    try:
        client = pymongo.MongoClient(mongo_uri)
        print("Connection to MongoDB successful")
        return client
    except pymongo.errors.ConnectionFailure as e:
        print(f"Connection failed: {e}")
        return None


def get_answer_with_retrieval(query: str, company_name: str) -> str:
    mongo_client = get_mongo_client(MONGODB_URI)

    vector_store = MongoDBAtlasVectorSearch(
        mongo_client,
        db_name=DB_NAME,
        collection_name=company_name,
        index_name="vector_index",
    )

    index = VectorStoreIndex.from_vector_store(vector_store)

    chat_engine = index.as_chat_engine(
        verbose=False,
        similarity_top_k=3,
        system_prompt=(system_prompt),
    )
    response = chat_engine.chat(query)

    print(response.response)

    return response.response


if __name__ == "__main__":
    get_answer_with_retrieval(
        company_name="mongodb", query="What is the product you're selling"
    )
