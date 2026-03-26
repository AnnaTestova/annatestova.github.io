from nltk.tokenize import sent_tokenize

def extract_text_from_file(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def split_into_sentences(text):
    return sent_tokenize(text)
