from apiclient.discovery import build
import json, os, webvtt, glob, sys
from configs import *


youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=DEVELOPER_KEY)

# retorna informações brutas do canal 
def youtube_channels(channel_id: str):
    print("Fazendo requisição do canal")
    channel_response = youtube.channels().list(
        part="id,snippet,statistics", id=channel_id).execute()

    return channel_response.get("items")[0]


# Lê o dado bruto do canal e coleta informações importantes
def channel_components(channel_data: dict):
    print("Coletando informações do canal")
    channel_infos = {}

    # id do canal
    channel_infos["channel_id"] = channel_data["id"]

    snippet = channel_data["snippet"]
    # nome do canal
    channel_infos["channel_name"] = snippet["title"]

    if channel_infos["channel_id"] in channels['right']:
        channel_type = "altright"
    elif channel_infos["channel_id"] in channels['left']:
        channel_type = "altleft"
    else:
        channel_type = ""
    # vertente do canal
    channel_infos["channel_type"] = channel_type

    statistics = channel_data["statistics"]
    # quantidade de visualizações do canal
    channel_infos["channelViewCount"] = statistics["viewCount"]
    # quantidade de inscritos do canal
    channel_infos["subscriberCount"] = statistics["subscriberCount"]
    
    return channel_infos


# concatena informações de canal e video e salva
def build_channel_video_file(channel_data: dict, video_data: dict, transcript: str):
    channel_useful_infos = channel_components(channel_data)
    video_useful_infos = video_components(video_data, transcript)
    video_useful_infos.update(channel_useful_infos)

    print("Salvando video...")
    writeToJSONFile(path="./channel_data/" + video_useful_infos['channel_id'], fileName=video_useful_infos['video_id'], data=video_useful_infos)


# retorna informações brutas do video 
def youtube_videos(video_id):
    print("Fazendo requisição do video")

    video_response = youtube.videos().list(
        part="id,snippet,recordingDetails,statistics,contentDetails", id=video_id, maxResults=50).execute()
    return video_response.get("items")[0]


# Lê o dado bruto do video e coleta informações importantes
def video_components(video_data: dict, transcript: str):
    print("Coletando informações do video")

    video_infos = {"transcript": transcript}

    # id do video
    video_infos["video_id"] = video_data["id"]
    # duração do video
    video_infos["video_duration"] = video_data["contentDetails"]["duration"][2:]

    snippet = video_data["snippet"]
    # titulo do video
    video_infos["video_title"] = snippet["title"]
    # descrição do video
    video_infos["video_desc"] = snippet["description"]
    # data de publicação do video
    video_infos["video_date"] = snippet["publishedAt"]
    # tags do video
    tags = snippet.get("tags")
    if tags == None:
        tags = []
    video_infos["tags"] = tags

    statistics = video_data["statistics"]
    # quantidade de visualizações do video
    video_infos["view_count"] = statistics["viewCount"]
    # quantidade de comentarios do video
    video_infos["comment_count"] = statistics.get("comment_count")
    # quantidade de aprovações do video
    likeCount = statistics.get("likeCount")
    if likeCount == None:
        likeCount = ""
    video_infos["like_count"] = likeCount
    # quantidade de desaprovações do video
    dislikeCount = statistics.get("dislikeCount")
    if dislikeCount == None:
        dislikeCount = ""
    video_infos["dislike_count"] = dislikeCount
    
    return video_infos


# retorna informações brutas de comentarios
def youtube_commentThread(video_id):
    print("Fazendo requisição dos comentarios")
    page_commentThread = []

    newPage = None
    while True:
        commentThread_response = youtube.commentThreads().list(
            part="id,snippet,replies", videoId=video_id, maxResults=100, pageToken=newPage).execute()

        #armazena os comentarios de uma pagina na lista e acessa a próxima
        page_commentThread.append(commentThread_response.get("items"))
        newPage = commentThread_response.get("nextPageToken")
        print("Nova página de comentarios:", newPage)

        if newPage == None:
            break
   
    return page_commentThread


# Lê o dado bruto de comentarios e coleta informações importantes
def comment_components(comment_pages, channel_id):
    print("Coletando informações dos comentarios")
    if comment_pages != []:
        for page in comment_pages:
            for comment in page:
                comment_info = {}

                # id do comentario
                comment_info['comment_id'] = comment["id"]

                snippet = comment["snippet"]["topLevelComment"]["snippet"]
                # comentario
                comment_info['comment_text'] = snippet["textDisplay"]
                # quantidade de aprovações
                comment_info['comment_like_count'] = snippet["likeCount"]
                # id do video
                comment_info['video_id'] = snippet["videoId"]
                # data de publicação
                comment_info['comment_date'] = snippet["publishedAt"]
                # quantidade de respostas
                comment_info['comment_reply_count'] = comment["snippet"]["totalReplyCount"]
                # id do autor
                if snippet.get('authorchannel_id') == None:
                    author_id = ""
                else:
                    author_id = snippet.get('authorchannel_id').get("value")
                comment_info['author_id'] = author_id
                
                print("salvando comentario", comment_info['comment_id'])
                writeToJSONFile("./channel_data/" + channel_id + "/comments", comment_info['comment_id'], comment_info)

                print("Pegando respostas e salvando...")
                if comment.get("replies") != None:
                    for reply in comment["replies"]["comments"]:
                        reply_info = {"parent_id": comment_info['comment_id'], "video_id": comment_info['video_id'], "comment_reply_count": 0}
                        # id da resposta
                        reply_info["comment_id"] = reply["id"]

                        snippet = reply["snippet"]
                        # data de publicação
                        reply_info['comment_date'] = snippet["publishedAt"]
                        # resposta
                        reply_info['comment_text'] = snippet["textDisplay"]
                        # quantidade de aprovações
                        reply_info['comment_like_count'] = snippet["likeCount"]
                        # id do autor
                        if snippet.get('authorchannel_id') == None:
                            author_id = ""
                        else:
                            author_id = snippet.get('authorchannel_id').get("value")
                        reply_info['author_id'] = author_id
                        
                        writeToJSONFile("./channel_data/" + channel_id + "/comments", reply_info["comment_id"], reply_info)


def writeToJSONFile(path: str, fileName: str, data: dict):
    filePathNameWExt = path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)


# retorna a transcrição do video
def getVTTTranscript(video_id: str):
    print("pegando a transcrição...")

    texto = ""
    URL = "https://www.youtube.com/watch?v=" + video_id

    max_tries = 3 
    while max_tries:
        os.system("youtube-dl --skip-download --write-auto-sub " + URL)
        transcript_file = glob.glob('*' + video_id + '.en.vtt')

        # Se não tiver sucesso em 3 tentativas, o texto retorna vazio
        if transcript_file == []:
            max_tries -= 1
        else:
            # Leitura do arquivo com a transcrição 
            vtt = webvtt.read(transcript_file[0])
            lines = []
            for z, line in enumerate(vtt):
                lines.extend(line.text.strip().splitlines())
                previous = None
            for x, line in enumerate(lines):
                if line == previous:
                    continue
                texto += " " + line
                previous = line

            os.remove(transcript_file[0])
            break
        
    return texto


# Retoma a lista de videos de onde parou
def verification_video(list_video_ids, last_video=None):
    if last_video:
        list_video_ids = list_video_ids[list_video_ids.index(last_video):]
    return list_video_ids


# Retoma a lista de canais de onde parou
def verification_channel(list_channels, last_channel=None):
    if last_channel:
        list_channels = list_channels[list_channels.index(last_channel):]
    return list_channels


def save_last_channel_video(channel, video):
    with open("./last_video_control.txt", "w") as f:
        f.write(f"{channel};{video}")


def load_last_channel_video():
    try:
        with open("./last_video_control.txt", "r") as f:
            text = f.read()
        return text.split(";")[0], text.split(";")[1]
    except:
        return None, None


if __name__ == "__main__":
    last_channel, last_video = load_last_channel_video()    

    list_channels = verification_channel(CHANNELS['right'] + CHANNELS['left'], last_channel)
    for i, channel_id in enumerate(list_channels):
        # Cria uma pasta referente ao canal para armazenar os dados, se não existir
        if not os.path.exists("./channel_data/" + channel_id):
            os.makedirs("./channel_data/" + channel_id)
        if not os.path.exists("./channel_data/" + channel_id + "/comments"):
            os.makedirs("./channel_data/" + channel_id + "/comments")

        # Armazena os ids dos videos em video_links
        videos = []
        try:
            with open("./video_links/" + channel_id + ".txt") as file:
                for line in file:
                    video_id = line.split("?v=")[1]
                    videos.append(video_id.strip("\n"))
        except:
            continue
        
        # Retoma a lista de videos de onde parou
        list_videos = verification_video(videos, last_video)
        #ultimo_video_id = None SALVAR ISSO EM ARQUIVO, ASSSIM COMO O ULTIMO CANAL

        print(f"{len(videos) - len(list_videos)} / {len(videos)}")
        print("Channel being processed:", channel_id)
        
        # Adquire informações brutas do canal
        channel_data = youtube_channels(channel_id)

        for i, video_id in enumerate(list_videos):
            save_last_channel_video(channel_id, video_id)

            print("video sendo processado: " + video_id)
            # Adquire a transcrição do video
            transcript = getVTTTranscript(video_id)
            try:
                # Aquisição de informações brutas do video 
                video_data = youtube_videos(video_id)
                # concatena os dados de canal e video, em seguida, grava 
                build_channel_video_file(channel_data, video_data, transcript)
                # Aquisição de informações brutas de comentarios 
                comment_data = youtube_commentThread(video_id)
                # Adquire informações importantes de comentarios e respostas, em seguida, grava
                comment_components(comment_data, channel_id)
                # Salva ultimo canal - video pro caso de acabar as requisições diárias. Sendo possível retornar no dia seguinte
            except Exception as e:
                if 'has disabled comments' in str(e) or "list index out of range" in str(e):
                    continue
                else:
                    print(e)
                    sys.exit(1)
            print("Video ja registrados: ", video_id)
