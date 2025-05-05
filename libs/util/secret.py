import os

DEFAULT_DATABASE_PATH = os.path.dirname(os.path.dirname(__file__)) + "/../llmops.db"
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
