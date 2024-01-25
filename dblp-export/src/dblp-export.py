import shutil

if __name__ == '__main__':
    print("Creating example files to be processed by dblp in /data/dblp-export/")
    shutil.copyfile("./files/example_output.tp", "/data/dblp-export/example_output.tp")
    shutil.copyfile("./files/tp.dtd", "/data/dblp-export/tp.dtd")