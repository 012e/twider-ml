from lib.qdrant.searcher import HybridSearcher

if __name__ == "__main__":
    query = input("Enter your search query: ")
    searcher = HybridSearcher("posts")
    results = searcher.search(query)
    print(results)

