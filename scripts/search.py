from app.searcher import HybridSearcher

def search():
    query = input("Enter your search query: ")
    searcher = HybridSearcher("posts")
    results = searcher.search(query)
    print(results)
