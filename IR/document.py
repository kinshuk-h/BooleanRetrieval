import re
import os
import io

from sortedcontainers import SortedSet, SortedDict
from abc  import ABC, abstractmethod
from docx import Document

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout    import LAParams
from pdfminer.pdfpage   import PDFPage

class Unit:
    __doc_id_count__ = 0

    @classmethod
    def genDocId(cls):
        cls.__doc_id_count__ += 1
        return cls.__doc_id_count__ - 1

    def __init__(self, file, unit_number):
        self.file = file; self.unit_number = unit_number; self.words = SortedSet([])
        self.docId = self.genDocId()

    def add(self, iterable): self.words.update(iterable)
    def keywords(self): return self.words
    def id(self): return self.docId
    def string(self): return "<"+str(self.docId)+", "+self.file+", unit "+str(self.unit_number)+">"
    
    def __lt__(self, unit): return self.docId < unit.docId

def __default_tokenizer__(text): 
        return [ word.lower().strip(" \f\v\r\b\t\n(){}[]<>#$^%*\"'_|=-+*/\\&^") for word in re.split(r"[\s.,;:?!]+", text) ]

class Preprocessor(ABC):
    def __init__(self, file, tokenizer = None):
        super().__init__()
        if not os.path.exists(file): raise Exception(f"{file}: no such file.")
        self.file = file; self.texts = []; self.tokenizer = __default_tokenizer__ if tokenizer is None else tokenizer

    @abstractmethod
    def read(self): pass

    def count(self): return len(self.texts)
    def text(self, unit_number = 0):
        return self.texts[unit_number] if unit_number < len(self.texts) else None
    def unit(self, unit_number = 0):
        if unit_number <= len(self.texts):
            unit = Unit(self.file, unit_number)
            unit.add(self.tokenizer(self.texts[unit_number]))
            return unit
        return None

class TextPreprocessor(Preprocessor):
    def read(self):
        with open(self.file, 'r+') as file:
            self.texts.append('\n'.join(file.readlines()))

class DocPreprocessor(Preprocessor):
    def read(self):
        doc = Document(self.file)
        for paragraph in doc.paragraphs:
            self.texts.append(paragraph.text)

class PDFPreprocessor(Preprocessor):
    def read(self):
        manager = PDFResourceManager(); stream = io.StringIO()
        converter = TextConverter(manager, stream, laparams=LAParams())
        interpreter = PDFPageInterpreter(manager, converter)
        for page in PDFPage.get_pages(open(self.file, 'rb')):
            interpreter.process_page(page)
            self.texts.append(stream.getvalue())
            stream.truncate(0); stream.seek(0)

def make_preprocessor(file, tokenizer = None):
    """ Constructs an appropriate preprocessor for a given file.

    :param `file`: Path of the file to be preprocessed.
    :param `tokenizer`: (function, optional) Tokenizer to use to extract words from the text. 
        If `None` is specified, a default method is used.

    :returns: a subtype of Preprocessor to appropriately handle the given file.
    """
    extension = file[file.rfind('.')+1:].lower()
    if extension:
        if extension == 'pdf': return PDFPreprocessor(file, tokenizer)
        elif extension == 'docx': return DocPreprocessor(file, tokenizer)
        else: return TextPreprocessor(file, tokenizer)
    return None

class Index:
    def __init__(self, tokenizer = None):
        self.postings = SortedDict(); self.unit_list = SortedSet(); self.unit_count = 0
        self.tokenizer = __default_tokenizer__ if tokenizer is None else tokenizer
    def add(self, unit: Unit):
        self.unit_count += 1
        if len(unit.keywords()) == 0: self.unit_count -= 1
        else: self.unit_list.add(unit)
        for word in unit.keywords():
            if word:
                if word in self.postings: self.postings[word].add(unit)
                else: self.postings[word] = SortedSet([unit])
    def count(self): return self.unit_count
    def search(self, query):
        """Searches given query inside the index.

            :param `query`: String to search. Can contain operators `('and', 'or', 'not')` to refine results.

            :returns: a list of document units that satisfy the given query.
        """
        tokens = self.tokenizer(query); result, sub_result = None, None; i = 0; 
        while i < len(tokens):
            # print("> Now on token", i, ":", tokens[i])
            if tokens[i] == 'not': 
                i += 1; sub_result = self.unit_list.difference(self.postings[tokens[i]]) if i<len(tokens) and tokens[i] in self.postings else self.unit_list
            else: sub_result = self.postings[tokens[i]] if i<len(tokens) and tokens[i] in self.postings else None
            if i<len(tokens) and (tokens[i] == 'and' or tokens[i] == 'or'):
                operator = tokens[i]; i += 1
                if tokens[i] == 'not': 
                    i += 1; sub_result = self.unit_list.difference(self.postings[tokens[i]]) if i<len(tokens) and tokens[i] in self.postings else self.unit_list
                else: sub_result = self.postings[tokens[i]] if i<len(tokens) and tokens[i] in self.postings else None
                if result is not None and sub_result is not None: 
                    if operator == 'and': result = result.intersection(sub_result)
                    else: result = result.union(sub_result)
            elif result is not None: 
                if sub_result is not None: result = result.union(sub_result)
            elif result is None: result = sub_result
            i += 1
        return result
    def keywords(self): return self.postings.keys()
    def __getitem__(self, word):
        return self.postings[word] if word in self.postings else None
