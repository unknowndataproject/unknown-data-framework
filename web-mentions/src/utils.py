import yaml


#define a dictionary to store config files
class AttDict(dict):
    def __init__(self,*args,**kwargs):
        super(AttDict,self).__init__(*args,**kwargs)
        self.__dict__ = self

#read the config file and return it as dictionary
def read_config(config_file):
    return AttDict(yaml.load(open(config_file,"r"),Loader = yaml.FullLoader))
