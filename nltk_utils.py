import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

# Ensure you have downloaded the required NLTK data files
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Initialize the lemmatizer and stop words
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def tokenize(text: str) -> list[str]:
    """Tokenize the input text into words."""
    return word_tokenize(text)

def remove_stopwords(tokens: list[str]) -> list[str]:
    """Remove stop words from the token list."""
    return [word for word in tokens if word.lower() not in stop_words]

def lemmatize(tokens: list[str]) -> list[str]:
    """Lemmatize the token list."""
    lemmatized_tokens = []
    for token, tag in pos_tag(tokens):
        pos = get_wordnet_pos(tag)
        lemmatized_tokens.append(lemmatizer.lemmatize(token, pos))
    return lemmatized_tokens

def get_wordnet_pos(treebank_tag: str) -> str:
    """Convert Treebank POS tag to WordNet POS tag."""
    if treebank_tag.startswith('J'):
        return 'a'  # Adjective
    elif treebank_tag.startswith('V'):
        return 'v'  # Verb
    elif treebank_tag.startswith('N'):
        return 'n'  # Noun
    elif treebank_tag.startswith('R'):
        return 'r'  # Adverb
    else:
        return 'n'  # Default to noun
