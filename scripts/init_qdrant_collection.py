# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "ml @ file:///${PROJECT_ROOT}/"
# ]
# ///

def main():
    from qdrant.init import create_collections_if_not_exists

    create_collections_if_not_exists()

if __name__ == "__main__":
    main()

