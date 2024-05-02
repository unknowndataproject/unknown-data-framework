import json
import pdb

from lxml import etree
from glob import glob
from pathlib import Path
from typing import Union, Optional, List, Dict

ns = dict(namespaces={"tei": "http://www.tei-c.org/ns/1.0"})
tei_prefix = "{http://www.tei-c.org/ns/1.0}"
xml_id = '{http://www.w3.org/XML/1998/namespace}id'

def transform_xml_folder(source_path: Path, target_path: Path, sentences=True) -> str:
    target_path_txt = target_path / Path("text_extracted")
    target_path_json = target_path / Path("text_extracted_json")
    target_path_txt.mkdir(parents=True, exist_ok=True)
    target_path_json.mkdir(parents=True, exist_ok=True)
    for file in glob(str(source_path) + "/*.xml"):
        text, annos = transform_xml(file, sentences)
        doc = dict(text=text, annotations=annos)
        fn = Path(file).stem
        fn = fn[:-4] if fn.endswith(".tei") else fn
        fn_txt = target_path_txt / Path(fn + ".txt")
        fn_json = target_path_json / Path(fn + ".json")
        fn_txt.open("w").write(text)
        json.dump(doc, fn_json.open("w"))

def transform_xml(filename, sentences=True):
    root = etree.parse(filename)
    extractor = TeiExtractor(root, sentences)
    doc, annotations = extractor.extract()
    return doc, annotations

class TeiExtractor:
    def __init__(self, root, sentences=True):
        self.text = ""
        self.annos = {}
        self.root = root
        self.sentences = sentences
       
    def extract(self):
        # reset current extraction
        self.text, self.annos = "", {}
        # header section
        self.add_extraction(self.get_title(), sep="")
        # doc = add_extraction(doc, get_authors(root), sep="")
        self.text += "\n"
        self.add_extraction(self.get_abstract(), sep="\n")
        self.text += "\n\nMain:\n"
        self.annos["SectionHeader"] = [dict(begin=0, end=len(self.text))]
        begin_main = len(self.text)
        self.add_extraction(self.get_body_divs(), sep="\n")
        self.annos["SectionMain"] = [dict(begin=begin_main, end=len(self.text))]
        self.text += "\n"
        self.add_extraction(self.get_footnotes(), sep="\n")
        self.text += "\n"
        self.add_extraction(self.get_references(), sep="\n")
        # add idx to each element
        for key_annos in self.annos.values():
            key_annos.sort(key=lambda x: (x["begin"], x["end"]))
            for idx, anno in enumerate(key_annos):
                anno["idx"] = idx
        return self.text, self.annos

    def add_extraction(self, new, sep=""):
        text, annos = _add_extraction(
            (self.text, self.annos),
            new, sep)
        self.text, self.annos = text, annos
        
    def get_title(self):
        xpath = "/tei:TEI/tei:teiHeader/tei:fileDesc/tei:titleStmt/tei:title"
        text, annos = "", {}
        title_ele = self.root.xpath(xpath, **ns)
        if title_ele:
            title, annos = self.get_text_with_refs(title_ele[0])
        return title, annos


    def get_abstract(self):
        xpath = "/tei:TEI/tei:teiHeader/tei:profileDesc/tei:abstract/tei:div"
        divs = self.root.xpath(xpath, **ns)
        text, annos = "Abstract:\n", {}
        #print("abstract")
        for idx, div in enumerate(divs):
            #print("div in abstract")
            div_content = self.get_div(div)
            #print("div in abstract after get_div")
            sep = "\n" if idx > 0 else ""
            text, annos = _add_extraction((text, annos), div_content, sep)
        annos["Abstract"] = [dict(begin=0, end=len(text))]
        #print("abstract finished")
        return text, annos

    def get_body_divs(self):
        xpath = "/tei:TEI/tei:text/tei:body/tei:div" # AAARRRGGG
        xpath = "/tei:TEI/tei:text/tei:body/tei:div"#text/body/tei:div"
        div_elements = self.root.xpath(xpath, **ns)
        content = ("", {})
        for div_element in div_elements:
            div_extraction = self.get_div(div_element)
            content = _add_extraction(content, div_extraction, "\n\n")
        return content

    def get_div(self, div_element):
        #print("get_div")
        text, annos = "", {}
        first_p = True
        for element in div_element:
            tag = element.tag.replace(tei_prefix, "")
            if tag == "head":
                begin = len(text)
                n = element.attrib.get("n")
                if n:
                    text += n + " "
                text += element.text 
                head_anno = dict(begin=begin, end=len(text))
                if n:
                    head_anno["n"] = n
                annos["Head"] = annos.get("Head", []) + [head_anno]
                text += "\n"
            elif tag == "formula":
                text += element.text
            elif tag == "p":
                #print("found p in div")
                paragraph = self.get_paragraph(element)
                content = (text, annos)
                sep = "" if first_p else "\n"
                text, annos = _add_extraction(content, paragraph, sep)
                first_p = False
            else:
                #print("not handled:", tag)
                pass
                #print(f"\r{element.tag} is not handled", end="")
        annos["Div"] = [dict(begin=0, end=len(text))]
        return text, annos

    def get_paragraph(self, element):
        #print("found para", element.tag)
        if not self.sentences:
            text, annos = self.get_text_with_refs(element)
        else:
            text, annos = self.get_sentences(element)
        #print(f"|{text}|")    
        annos["Paragraph"] = [dict(begin=0, end=len(text))]
        return text, annos

    def get_sentences(self, element):
        text, annos = "", {}
        for idx, sent in enumerate(element):
            if idx != 0:
                text += " "
            sent_text, sent_annos = self.get_text_with_refs(sent)
            sent_annos["Sentence"] = [dict(begin=0, end=len(sent_text))]
            if sent_text:
                text, annos = _add_extraction((text, annos),
                                                   (sent_text, sent_annos))
        return text, annos


    def get_footnotes(self):
        text, annos = "Footnotes:", {}
        footnotes = self.root.xpath("//tei:text/tei:body/tei:note", **ns)
        for footnote in footnotes:
            text += "\n"
            ident = footnote.attrib.get(xml_id)
            n = footnote.attrib.get('n')
            if n:
                footnote_start = (f"{n}: ", {})
            else:
                footnote_start = ("", {})
            footnote_text = self.get_text_with_refs(footnote)
            footnote_text, footnote_annos = _add_extraction(footnote_start, footnote_text)
            footnote_anno = dict(begin=0, end=len(footnote_text))
            if ident:
                footnote_anno["id"] = ident
            if n:
                footnote_anno["n"] = n
            footnote_annos["Footnote"] = [footnote_anno]
            text, annos = _add_extraction((text, annos), (footnote_text, footnote_annos))
        annos["SectionFootnote"] = [dict(begin=0, end=len(text))]
        return text, annos


    def get_references(self):
        # div[type="references"] ?
        xpath = "/tei:TEI/tei:text/tei:back/tei:div/tei:listBibl/tei:biblStruct"
        references = self.root.xpath(xpath, **ns)
        text = "References:\n\n"
        annos = {}
        for idx, ref in enumerate(references):
            ident = ref.attrib.get(xml_id)
            notes = ref.xpath("./tei:note[@type='raw_reference']", **ns)
            ref_text = ""
            for note in notes:
                if note.text:
                    text += "- "
                    ref_text += note.text.strip()
            if ref_text or ident:
                ref_anno = dict(begin=0, end=len(ref_text))
                if ident:
                    ref_anno["id"] = ident
                ref_annos = dict(ReferenceString=[ref_anno])
                text, annos = _add_extraction((text, annos), (ref_text, ref_annos), "")
                if idx > 0:
                    text += "\n\n"
        annos["SectionReference"] = [dict(begin=0, end=len(text))]
        return text, annos

    def get_text_with_refs(self, element):
        #print(f"get Text from {element.tag}")
        text, annos = "", {}
        if element.text and element.text.strip():
            text += element.text.strip()
        with_ref = False
        for child in element:
            tag = child.tag.replace(tei_prefix, "")
            if tag == "ref":
                text_ref = child.text.strip() if child.text is not None else ""
                ref_type = child.attrib.get("type")
                target = child.attrib.get("target")
                if ref_type == "bibr":
                    ref_type = "ReferenceToBib"
                elif ref_type == "foot":
                    ref_type = "ReferenceToFootnote"
                elif ref_type == "figure":
                    ref_type = "ReferenceToFigure"
                elif ref_type == "table":
                    ref_type = "ReferenceToTable"
                elif ref_type == "formula":
                    ref_type = "ReferenceToFormula"
                else:
                    #print(ref_type + " not known")
                    ref_type = "ReferenceUnknown"
                child_anno = dict(begin=0, end=len(text_ref))
                if target:
                    child_anno["target"] = target
                child_annos = {ref_type: [child_anno]}
                if text_ref and text_ref[0] not in ",;.!?)]":
                    text += " "
                text, annos = _add_extraction((text, annos),
                                                   (text_ref, child_annos))
                if child.tail and child.tail.strip():
                    tail_text = child.tail.strip()
                    if tail_text[0] not in ",;.!?)]":
                        text += " "
                    text += child.tail.strip()
            else:
                #print(tag, "not known")
                pass
            #print(etree.tostring(child))
            #text = text[:text.rfind("\n")]
            #if child.text:
            #    text += child.text[:child.text.rfind("\n") if "\n" in child.text else None]
            #if child.tail is not None:
            #    text += child.tail[:child.tail.rfind("\n") if "\n" in child.tail else None]
            #with_ref = True
        #print(text)
        return text, annos
    
def _add_extraction(old, new, sep=""):
    offset = 0
    text, annos = old
    new_text, new_annos = new
    if new_text:
        text += sep 
        offset = len(text)
        text += new_text
    annos_updated = {}
    keys = set(annos) | set(new_annos)
    for key in keys:
        annos_key_old = annos.get(key, [])
        annos_key_new = new_annos.get(key, [])
        [a.update(dict(
            begin=a["begin"] + offset,
            end=a["end"] + offset)
                 )
         for a in annos_key_new]
        annos_key_all = annos_key_old + annos_key_new
        annos_key_all.sort(key=lambda x: (x["begin"], ["x.end"]))
        annos_updated[key] = annos_key_all
    return text, annos_updated
