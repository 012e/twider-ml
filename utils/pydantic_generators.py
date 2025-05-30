
def to_pascal_case(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


