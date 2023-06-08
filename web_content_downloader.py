import os
import tkinter as tk

import pdfkit
import pytube


def download_main():
    video_urls = [i.strip() for i in text_widget.get("1.0", "end-1c").split("\n") if len(i.strip()) > 1]
    [print(f"{i + 1}. {elem}") for i, elem in enumerate(video_urls)]
    for url in video_urls:
        if "youtube.com/watch?v=" in url:
            ytc = _get_video_info(url)
            ytc.streams.get_highest_resolution().download(DIR)
            print("Video Downloaded")
        else:
            _download_webpage(url)


def _download_webpage(link):
    PATH_WKHTMLTOPDF = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=PATH_WKHTMLTOPDF)
    pdfkit.from_url(url=link, output_path=fr"{DIR}\webpage.pdf", configuration=config)
    print(f"{link} saved as PDF")


def _get_video_info(link):
    ytc = pytube.YouTube(url=link)
    ytc_info = ytc.vid_info
    print(f"\"{ytc_info['videoDetails']['title']}\" by {ytc_info['videoDetails']['author']}", end=", ")
    print(f"{format(int(ytc_info['videoDetails']['viewCount']), ',d')} views, ", end="")
    print(f"{ytc_info['videoDetails']['lengthSeconds']}s, {ytc.publish_date}")
    return ytc


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
