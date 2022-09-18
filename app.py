from re import search
from flask import Flask, render_template, jsonify, request, redirect, session, make_response
from flask_cors import CORS, cross_origin
from pytube.extract import video_info_url
from youtubesearchpython import Suggestions, ResultMode
from youtube_search import YoutubeSearch
import youtube_dl
import os
import json
import random
import requests
from stuff import ran_quote, time_cal

app = Flask(__name__)
CORS(app, support_credentials=True)

@app.route('/watch', methods =["GET", "POST"])
def play():
    video_url_raw = request.values.get("v")
    video_url = f'https://www.youtube.com/watch?v={video_url_raw}'
    def video_info_spider(url):
        options = {"no_warnings": True, "quiet": True}
        with youtube_dl.YoutubeDL(options) as ytdl:
            try:
                video_info = ytdl.extract_info(url, download=False)
                video_description = description_formatter(video_info["description"])
                video_url_stream = [video_info["formats"][-1]["url"], video_info["formats"][-2]["url"], video_info["formats"][-3]["url"]]
                audio_url_stream = [video_info["requested_formats"][1]["url"], video_info["formats"][1]["url"]]
                video_thumnail = video_info['thumbnails'][-1]['url']
                return [video_info, video_description, video_url_stream, audio_url_stream, video_thumnail]
            except:
                video_url_piped = f'https://pipedapi.kavin.rocks/streams/{video_url_raw}'
                video_info_raw = json.loads(requests.get(video_url_piped).content)
                video_info = {
                "description": video_info_raw["description"],
                "title": video_info_raw["title"],
                "channel_url": f'https://youtube.com{video_info_raw["uploaderUrl"]}',
                "view_count": video_info_raw["views"],
                "like_count": video_info_raw["likes"]
                }
                video_description = description_formatter(video_info["description"])
                video_url_stream = [video_info_raw["videoStreams"][11]["url"], video_info_raw["videoStreams"][10]["url"]]
                audio_url_stream = [video_info_raw["audioStreams"][1]["url"]]
                video_thumnail = video_info_raw["thumbnailUrl"]
                return [video_info, video_description, video_url_stream, audio_url_stream, video_thumnail]
    def description_formatter(desc):
        desc = desc.split("\n")
        # des_raw = desc.split(" ")
        return desc
    video_content = video_info_spider(video_url)
    return render_template("play.html", url=video_url, url_stream=video_content[2], url_info=video_content[0], url_thumnail=video_content[4], url_id=video_url_raw, url_audio_stream=video_content[3], url_description=video_content[1])

@app.route('/download', methods =["GET", "POST"])
@cross_origin(supports_credentials=True)
def download():
    video_url = request.values.get("url")
    video_url_raw = str(video_url).replace("https://www.youtube.com/watch?v=", "")
    def video_info_spider(url):
        options = {"no_warnings": True, "quiet": True}
        with youtube_dl.YoutubeDL(options) as ytdl:
            try:
                video_info = ytdl.extract_info(url, download=False)
                video_description = description_formatter(video_info["description"])
                video_url_stream = [video_info["formats"][-1]["url"], video_info["formats"][-2]["url"], video_info["formats"][-3]["url"]]
                audio_url_stream = [video_info["requested_formats"][1]["url"], video_info["formats"][1]["url"]]
                video_thumnail = video_info['thumbnails'][-1]['url']
                return [video_info, video_description, video_url_stream, audio_url_stream, video_thumnail]
            except:
                video_url_piped = f'https://pipedapi.kavin.rocks/streams/{video_url_raw}'
                video_info_raw = json.loads(requests.get(video_url_piped).content)
                video_info = {
                "description": video_info_raw["description"],
                "title": video_info_raw["title"],
                "channel_url": f'https://youtube.com{video_info_raw["uploaderUrl"]}',
                "view_count": video_info_raw["views"],
                "like_count": video_info_raw["likes"]
                }
                video_description = description_formatter(video_info["description"])
                video_url_stream = [video_info_raw["videoStreams"][11]["url"], video_info_raw["videoStreams"][10]["url"]]
                audio_url_stream = [video_info_raw["audioStreams"][1]["url"]]
                video_thumnail = video_info_raw["thumbnailUrl"]
                return [video_info, video_description, video_url_stream, audio_url_stream, video_thumnail]
    def description_formatter(desc):
        desc = desc.split("\n")
        # des_raw = desc.split(" ")
        return desc
    video_content = video_info_spider(video_url)
    download_stuff = {"url": video_url, "url_stream": video_content[2], "url_info": video_content[0], "url_thumnail": video_content[4], "url_id": video_url_raw, "url_audio_stream": video_content[3], "url_description": video_content[1]}
    return jsonify(download_stuff)

@app.route('/listen/<audio_url_raw>')
def listen(audio_url_raw):
    audio_url = f'https://www.youtube.com/watch?v={audio_url_raw}'
    def audio_info_spider(url):
        options = {"no_warnings": True, "quiet": True}
        with youtube_dl.YoutubeDL(options) as ytdl:
            audio_info = ytdl.extract_info(url, download=False)
            return audio_info
    def description_formatter(desc):
        desc_raw = desc.replace("/n", "<br>")
        return desc_raw
    audio_info = audio_info_spider(str(audio_url))
    audio_description = description_formatter(audio_info["description"])
    video_url_stream = audio_info["formats"][-1]["url"]
    audio_url_stream = audio_info["formats"][0]["url"]
    return render_template("listen.html", url=audio_url,url_stream=video_url_stream, url_info=audio_info, url_id=audio_url_raw, url_audio_stream=audio_url_stream, url_description=audio_description)

@app.route('/suggest/<query>', methods =["GET", "POST"])
def suggest_spider(query):
    query_suggestions = Suggestions(language = 'en', region = 'us')
    suggestions = query_suggestions.get(query, mode = ResultMode.json)
    return suggestions

@app.route('/results_temp', methods =["GET", "POST"])
def search_provider():
    search_term = request.values.get("search_query")
    url = f'/results?search_query={search_term}'
    search_response = make_response(redirect(url))
    search_response.set_cookie('last_search', search_term)
    search_response.set_cookie('response_origin', "This cookie does nothing :)")
    search_response.set_cookie('time', time_cal())
    return search_response

@app.route('/results', methods =["GET", "POST"])
def search_show():
    search_term = request.values.get("search_query")
    if "youtube.com/watch" in search_term:
        return redirect(str(search_term).replace("www.youtube.com", "ytspider.herokuapp.com"))
    if "youtube.com" in search_term:
        return redirect(str(search_term).replace("youtube.com/", "ytspider.herokuapp.com/watch?v="))
    if "youtu.be" in search_term:
        return redirect(str(search_term).replace("youtu.be/", "ytspider.herokuapp.com/watch?v="))
    def results_spider(search_term):
        results = YoutubeSearch(search_term, max_results=30).to_dict()
        return results
    search_info = results_spider(search_term)
    return render_template("search.html", items=search_info, search_title=search_term.capitalize())

@app.route('/channel/<channel_id>')
def channel_about(channel_id):
    def channel_spider(id_):
        import requests
        channel_page = json.loads(requests.get(f'https://pipedapi.kavin.rocks/channel/{id_}').content)
        return channel_page
    return render_template("channel.html", id_info=channel_spider(channel_id))

@app.route('/c/<channel>')
def channel_info(channel):
    def channel_spider(c):
        import requests
        channel_page = json.loads(requests.get(f'https://pipedapi.kavin.rocks/c/{c}').content)
        try:
            if channel_page["message"] == 'Not found (\"404 \")':
                    channel_page = json.loads(requests.get(f'https://pipedapi.kavin.rocks/user/{c.upper()}').content)
        except:
            pass
        return channel_page
    return render_template("channel.html", id_info=channel_spider(channel))

@app.route('/credits')
def credits_page():
    credits_list=["https://simpleicons.org/", "https://www.heroku.com/", "https://github.com/joetats/youtube_search", "https://github.com/alexmercerind/youtube-search-python", "https://flask.palletsprojects.com/en/", "https://newtoallofthis123.github.io/About", "https://github.com/pytube/pytube", "https://github.com", "https://youtube.com", "https://pypi.org/project/ytps/", "https://realfavicongenerator.net/"]
    return render_template("credits.html", urls=credits_list)

@app.route('/license')
def license_page():
    return render_template("license.html")

@app.route('/about')
def about_page():
    return render_template("about.html")

@app.route('/quotes')
def quotes():
    ran_quotes = [ran_quote(), ran_quote(), ran_quote(), ran_quote(), ran_quote(), ran_quote()]
    return render_template("sincere.html", ran_quotes=ran_quotes)

@app.route('/video', methods=["GET"])
def video():
    video_list = ["9bOfryhXCOk", "Qv1d9VyDrGY", "sORgN0I5RAY", "8124kv-632k"]
    video = random.choice(video_list)
    video_content=  f'<iframe width="1200" height="640" src="https://www.youtube-nocookie.com/embed/{video}?start=521&rel=0" title="YouTube video player" frameborder="0" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowtransparency allowfullscreen></iframe>'
    video_info = {"content": video_content}
    return video_info

def piped_pipe(region):
    import requests
    trending_page = json.loads(requests.get(f'https://pipedapi.kavin.rocks/trending?region=US').content)
    return trending_page

@app.route("/")
def hello_world():
    trending_page = piped_pipe("US")
    last_access = request.cookies.get('time')
    last_s = request.cookies.get('last_search')
    page_response = make_response(render_template('home.html', trend=trending_page, ran_quote=ran_quote(), last_details=[last_access, last_s]))
    return page_response

if __name__ == "__main__":
    app.run(debug=True, port=3000)
