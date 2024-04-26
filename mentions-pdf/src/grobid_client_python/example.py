from grobid_client.grobid_client import GrobidClient

if __name__ == "__main__":
    client = GrobidClient(config_path="./config.json")
    client.process("processFulltextDocument", "./resources/in_pdfs", output="./resources/out_tei", consolidate_citations=True, tei_coordinates=True, force=True,segment_sentences=True)
