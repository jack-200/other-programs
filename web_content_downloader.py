import json
import os
import tkinter as tk

import pdfkit
import pyperclip
import pytube
import requests
from bs4 import BeautifulSoup


def download_main():
    video_urls = [i.strip() for i in text_widget.get("1.0", "end-1c").split("\n") if len(i.strip()) > 1]
    [print(f"{i + 1}. {elem}") for i, elem in enumerate(video_urls)]
    for url in video_urls:
        if "youtube.com/watch?v=" in url:
            ytc = _get_video_info(url)
            ytc.streams.get_highest_resolution().download(DIR)
            print(f"Video Downloaded in {ytc.streams.get_highest_resolution().resolution}")
        elif "youtube.com/playlist?list=" in url:
            _get_playlist_info(url)
        else:
            _download_webpage(url)


def _get_video_info(link):
    ytc = pytube.YouTube(url=link)
    ytc_info = ytc.vid_info
    print(f"\"{ytc_info['videoDetails']['title']}\" by {ytc_info['videoDetails']['author']}", end=", ")
    print(f"{format(int(ytc_info['videoDetails']['viewCount']), ',d')} views, ", end="")
    print(f"{ytc_info['videoDetails']['lengthSeconds']}s, {ytc.publish_date.strftime('%Y-%m-%d')}")
    return ytc


def _get_playlist_info(link):
    response = requests.get(link)
    response = BeautifulSoup(response.content, "html.parser").prettify()

    yt_data = response.replace('"', "`")
    yt_data = next(line for line in yt_data.split("\n") if "var ytInitialData = " in line)[23:-1]
    yt_data = json.loads(yt_data.replace("`", '"'))
    yt_data = yt_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"][
        "sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"][
        "contents"]

    video_urls = []
    print(f"{len(yt_data)} YouTube videos")
    for video in yt_data:
        title = video["playlistVideoRenderer"]["title"]["runs"][0]["text"]
        video_url = f'https://www.youtube.com/watch?v={video["playlistVideoRenderer"]["videoId"]}'
        video_urls.append(video_url)
        print(f"{title}, {video_url}")
    pyperclip.copy("\n".join(video_urls))
    print(f"{len(video_urls)} YouTube links copied to clipboard")


def _download_webpage(link):
    path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_url(url=link, output_path=fr"{DIR}\webpage.pdf", configuration=config)
    print(f"{link} saved as PDF")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Web Content Downloader")
    root.geometry("600x300")
    root.config(bg="#1E1E1E")
    root.resizable(width=False, height=False)
    tk.Label(root, text=" Web Content Downloader ", font="arial 20 bold", fg="#FFFFFF", bg="#464646", ).pack()
    tk.Label(root, text="Paste Link(s) Here:", font="arial 15 bold", fg="Black", bg="#EC7063", ).place(x=5, y=50)

    text_widget = tk.Text(root, height=10, width=70)
    text_widget.place(x=5, y=90)

    scrollbar = tk.Scrollbar(root)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar.config(command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar.set)
    DIR = os.path.dirname(os.path.abspath(__file__))
    tk.Button(root, text="DOWNLOAD", font="arial 15 bold", fg="white", bg="#ff0000", padx=2,
              command=download_main, ).place(x=330, y=45)

    root.mainloop()
