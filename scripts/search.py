# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ml @ file:///${PROJECT_ROOT}/"
# ]
# ///

from qdrant.searcher import HybridSearcher

if __name__ == "__main__":
    query = input("Enter your search query: ")
    searcher = HybridSearcher("posts")
    results = searcher.search(query)
    print(results)

