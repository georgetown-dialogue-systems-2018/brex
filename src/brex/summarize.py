import brex.config as cfg

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from sumy.summarizers.lsa import LsaSummarizer as Summarizer


LANGUAGE = cfg.summarization_language
SENTENCES_COUNT = cfg.summarization_sentence_count

def summarize(s, sentence_count=SENTENCES_COUNT):
    # or for plain text files
    parser = PlaintextParser.from_string(s, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    return " ".join([str(sentence) for sentence in summarizer(parser.document, sentence_count)])
