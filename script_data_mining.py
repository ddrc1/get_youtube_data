from apiclient.discovery import build
import json, os, webvtt, glob, sys

DEVELOPER_KEY = "AIzaSyDVSOML90GcYq7ZVD_sC1aMLty6Gu6Ngqs" #Chave pessoal da api
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def youtube_channels(YOUTUBE_CHANNEL_ID):
    channel_response = youtube.channels().list(
        part="id,snippet,statistics", id=YOUTUBE_CHANNEL_ID).execute()
    return channel_response.get("items")[0]


def components_channels(channel_response_items, video_components):
    id = channel_response_items["id"]
    snippet = channel_response_items["snippet"]
    name = snippet["title"]
    right = ["UCrcrV4J6exbyTY4gcbvL_lA", "UCC3L8QaxqEGUiBC252GHy3w", "UC0uVZd8N7FfIZnPu0y7o95A", "UCittVh8imKanO_5KohzDbpg", "UCN0-RRaxMgh86eOwndAklxw", "UCmrLCXSDScliR7q8AxxjvXg", "UCnQC_G5Xsjhp9fEJKuIcrSw"]
    left = ["UCHuLYgw4dGbC2BuZQqPWV1g", "UCDG73pGqESS1XcEVY_0xwWw", "UCVY0aIaw-V9GbWmlab4Z_dw", "UCTG-iJm0HtjWVOAwN8sA4Xg", "UCCvdjsJtifsZoShjcAAHZpA",
            "UCOVUyXd-d5P-hznNF9zJQ-g", "UCidbCSNfzJXScnt8LWtwrhA", "UCCT8a7d6S6RJUivBgNRsiYg", "UC2PA-AKmVpU6NKCGtZq_rKQ", "CT5jxI_OYY2r--TjAGXD03A", "C5fdssPqmmGhkhsJi4VcckA",
            "UCJ6o36XL0CpYb6U5dNBiXHQ", "UCNvsIonJdJ5E4EXMa65VYpA"]
    if id in right:
        channel_type = "altright"
    elif id in left:
        channel_type = "altleft"
    else:
        channel_type = ""
    statistics = channel_response_items["statistics"]
    viewCount = statistics["viewCount"]
    subscriberCount = statistics["subscriberCount"]
    arquivo = {"channel_name": name,
               "channelViewCount": viewCount,
               "subscriberCount": subscriberCount,
               "tags": video_components[2],
               "like_count": video_components[4],
               "transcript": video_components[6],
               "video_desc": video_components[7],
               "video_duration": video_components[8],
               "channel_type": channel_type,
               "dislike_count": video_components[5],
               "video_date": video_components[10],
               "channel_id": id,
               "video_title": video_components[1],
               "view_count": video_components[3],
               "video_id": video_components[0],
               "comment_count": video_components[9]}
    print(arquivo)
    writeToJSONFile(".\\canais_json\\" + id, video_components[0], arquivo)
    return channel_type


def components_activities(pages_activities):
    print("entrou no activity util")
    list_videos_id = []
    for page in pages_activities:
        for items_list in page:
            aux = items_list["contentDetails"]
            while type(aux) == dict and 'videoId' not in aux.keys():
                aux = aux[list(aux.keys())[0]]
            if type(aux) == dict:
                list_videos_id.append(aux['videoId'])
    return list_videos_id


def youtube_videos(YOUTUBE_VIDEO_ID):
    print("entrou no videos")
    video_response = youtube.videos().list(
        part="id,snippet,recordingDetails,statistics,contentDetails", id=YOUTUBE_VIDEO_ID, maxResults=50).execute()
    return video_response.get("items")[0]


def components_videos(video_response_items, transcript):
    print("entrou no video util")
    id = video_response_items["id"]
    video_duration = video_response_items["contentDetails"]["duration"][2:]
    snippet = video_response_items["snippet"]
    title = snippet["title"]
    description = snippet["description"]
    tags = snippet.get("tags")
    if tags == None:
        tags = []
    statistics = video_response_items["statistics"]
    viewCount = statistics["viewCount"]
    comment_count = snippet.get("comment_count")
    if tags == None:
        tags = ""
    likeCount = statistics.get("likeCount")
    dislikeCount = statistics.get("dislikeCount")
    if likeCount == None:
        likeCount = ""
    if dislikeCount == None:
        dislikeCount = ""
    video_date = snippet["publishedAt"]
    return [id, title, tags, viewCount, likeCount, dislikeCount, transcript, description, video_duration, comment_count, video_date] # nao baixar comentario de o comment_count for 0


def youtube_commentThread(YOUTUBE_VIDEO_ID):
    print("entrou no comentario")
    page_commentThread = []
    # try:
    commentThread_response = youtube.commentThreads().list(
        part="id,snippet,replies", videoId=YOUTUBE_VIDEO_ID, maxResults=100).execute()
    page_commentThread.append(commentThread_response.get("items"))
    newPage = commentThread_response.get("nextPageToken")
    print(newPage)
    while newPage != None:
        commentThread_response = youtube.commentThreads().list(
            part="id,snippet,replies", videoId=YOUTUBE_VIDEO_ID, maxResults=100, pageToken=newPage).execute()
        newPage = commentThread_response.get("nextPageToken")
        page_commentThread.append(commentThread_response.get("items"))
        print(newPage)
    # except:
    #     pass
    return page_commentThread


def components_commentThread(page_commentThread_items, channel_id, channel_type):
    print("entrou no comentario util")
    if page_commentThread_items != []:
        for page in page_commentThread_items:
            for comment in page:
                id = comment["id"]
                snippet = comment["snippet"]["topLevelComment"]["snippet"]
                comment_text = snippet["textDisplay"]
                comment_like_count = snippet["likeCount"]
                video_id = snippet["videoId"]
                publishedAtCommentThread = snippet["publishedAt"]
                if snippet.get('authorChannelId') == None:
                    author_id = ""
                else:
                    author_id = snippet.get('authorChannelId').get("value")
                comment_reply_count = comment["snippet"]["totalReplyCount"]
                arquivo_comment = {"parent_id": "null",
                                   "comment_like_count": comment_like_count,
                                   "comment_date": publishedAtCommentThread,
                                   "channel_type": channel_type,
                                   "video_id": video_id,
                                   "comment_id": id,
                                   "comment_reply_count": comment_reply_count,
                                   "author_id": author_id,
                                   "comment_text": comment_text,
                                   "channel_id": channel_id}
                writeToJSONFile(".\\Canais_json\\" + channel_id + "\\comments", id, arquivo_comment)
                if comment.get("replies") != None:
                    for reply in comment["replies"]["comments"]:
                        id_reply = reply["id"]
                        snippet = reply["snippet"]
                        comment_date_reply = snippet["publishedAt"]
                        comment_text = snippet["textDisplay"]
                        if snippet.get('authorChannelId') == None:
                            author_id = ""
                        else:
                            author_id = snippet.get('authorChannelId').get("value")
                        comment_like_count_reply = snippet["likeCount"]
                        arquivo_reply = {"parent_id": id,
                                         "comment_like_count": comment_like_count_reply,
                                         "comment_date": comment_date_reply,
                                         "video_id": video_id,
                                         "channel_type": channel_type,
                                         "comment_id": id_reply,
                                         "comment_reply_count": 0,
                                         "author_id": author_id,
                                         "comment_text": comment_text,
                                         "channel_id": channel_id}
                        writeToJSONFile(".\\canais_json\\" + channel_id + "\\comments", id_reply, arquivo_reply)


def writeToJSONFile(path, fileName, data):
    filePathNameWExt = path + '/' + fileName + '.json'
    with open(filePathNameWExt, 'w') as fp:
        json.dump(data, fp, sort_keys=True, indent=4)


def getVTTTranscript(videoId):
    print("transcript")
    texto = ""
    URL = "https://www.youtube.com/watch?v=" + videoId
    os.system("youtube-dl --skip-download --write-auto-sub " + URL)
    file = glob.glob('*' + videoId + '.en.vtt')
    if file == []:
        URL = "https://www.youtube.com/watch?v=" + videoId
        os.system("youtube-dl --skip-download --write-auto-sub " + URL)
        file = glob.glob('*' + videoId + '.en.vtt')
    if file != []:
        vtt = webvtt.read(file[0])
        lines = []
        for z, line in enumerate(vtt):
            lines.extend(line.text.strip().splitlines())
            previous = None
        for x, line in enumerate(lines):
            if line == previous:
                continue
            texto += " " + line
            previous = line
        os.remove(file[0])
    return texto


def verificacao(list_videos_id_temp, ultimo_video_baixado = None):
    chave = True
    if ultimo_video_baixado != None:
        chave = False
    list_videos_id = []
    for i in range(len(list_videos_id_temp)):
        if chave:
            if i > 0 and list_videos_id_temp[i] != list_videos_id_temp[i - 1]:
                list_videos_id.append(list_videos_id_temp[i])
        elif list_videos_id_temp[i] == ultimo_video_baixado:
            chave = True
            list_videos_id.append(list_videos_id_temp[i])
    return list_videos_id


def main():
    ultimo_video_id = None #Colocar o ultimo video gerado entre aspas
    list_channels = ["UCsXVk37bltHxD1rDPwtNM8Q", "UC-lHJZR3Gqxm24_Vd_AJ5Yw", "UCONd1SNf3_QqjzjCVsURNuA", "UC5nc_ZtjKW1htCVZVRxlQAQ", "UC-kIKjS3gUFvsi4YoxveiWA",
					"UC2-_WWPT_124iN6jiym4fOw", "UC_GQ4mac4oN3wl1UdbFuTEA"]
    for channelId in list_channels:
        file = open(".\\canais_files\\" + channelId)
        if not os.path.exists(".\\canais_json\\" + channelId):
            os.makedirs(".\\canais_json\\" + channelId)
        if not os.path.exists(".\\canais_json\\" + channelId + "\\comments"):
            os.makedirs(".\\canais_json\\" + channelId + "\\comments")
        videos = []
        for line in file:
            videoId = line.split("?v=")[1]
            videos.append(videoId.strip("\n"))
        print(videos)
        list_videos_id = verificacao(videos, ultimo_video_id)
        ultimo_video_id = None
        print(list_videos_id)
        print(str(len(videos) - len(list_videos_id)) + "/" + str(len(videos)))
        print("Canal sendo registrado: ", channelId)
        channel_response_items = youtube_channels(channelId)
        for i in range(len(list_videos_id)):
            print("video sendo processado: " + str(list_videos_id[i]))
            transcript = getVTTTranscript(list_videos_id[i])
            try:
                channel_type = components_channels(channel_response_items, components_videos(youtube_videos(list_videos_id[i]), transcript))
                components_commentThread(youtube_commentThread(list_videos_id[i]), channelId, channel_type)
            except Exception as e:
                if 'has disabled comments' in str(e) or "list index out of range" in str(e):
                    continue
                else:
                    print(e)
                    sys.exit(1)
            print("Video ja registrados: ", list_videos_id[i])



main()
