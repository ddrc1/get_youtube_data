import os, json

path = '.\\canais_json'
directory = '.\\'
separador = "\\"
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for arq in f:
        if ".json" in arq and len(d) > 0:
            with open(directory + 'video.jsonl', 'a+') as outfile:
                file_json = open(str(r) + separador + str(arq), 'r')
                datastore = json.load(file_json)
                json.dump(datastore, outfile)
                outfile.write("\n")
            print("gravando video")
        elif ".json" in arq and not d:
            with open(directory + 'comment.jsonl', 'a+') as outfile:
                file_json = open(str(r) + separador + str(arq), 'r')
                datastore = json.load(file_json)
                json.dump(datastore, outfile)
                outfile.write("\n")
            print("gravando comentario")
