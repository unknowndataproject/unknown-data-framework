
import json

from pathlib import Path
from .extract_parts import generate_line_annos

class FlatTeiSeparateLoader:
    def __init__(self, txt_path, anno_path):
        self.txt_path = txt_path
        self.anno_path = anno_path

    def load_flat_tei(self, document_name):
        annos = []
        text  = ""
        path_text = Path(self.txt_path) / Path(document_name)
        path_anno = Path(self.anno_path) / Path(document_name).with_suffix(".json")
        text = path_text.open().read()
        annos = json.load(path_anno.open())
        return dict(text=text, annotations=annos)

class FlatTeiLoader:
    def __init__(self, pub_path):
        self.pub_path = Path(pub_path)

    def load_flat_tei(self, document_name):
        """ 
        parameters: document_name identifier of document 
        """
        file_path = self.pub_path / Path(document_name).with_suffix(".json")
        doc = json.load(file_path.open())
        doc["annotations"]["Line"] = generate_line_annos(doc["text"])
        return doc

