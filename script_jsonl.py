import os, json

def save_jsonl(outfile, path):
    file_json = open(path, 'r')
    datastore = json.load(file_json)
    json.dump(datastore, outfile)
    outfile.write("\n")


path = './channel_data'
directory = './jsonl_data/'

if not os.path.exists(directory):
    os.mkdir(directory)
    
# r=root, d=directories, f = files
print("Montando arquivos...")
for r, d, f in os.walk(path):
    for arq in f:
        if ".json" in arq and len(d) > 0:
            with open(directory + 'video.jsonl', 'a+') as outfile:
                save_jsonl(outfile, str(r) + "/" + str(arq))
        elif ".json" in arq and not d:
            with open(directory + 'comment.jsonl', 'a+') as outfile:
                save_jsonl(outfile, str(r) + "/" + str(arq))
print("Terminado")
