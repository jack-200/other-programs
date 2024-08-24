import json
import os
import pdfkit
import pyperclip
import pytube
import requests
import subprocess
import tkinter as tk
from bs4 import BeautifulSoup


def download_main():
    # Extract video URLs from the text widget
    video_urls = [i.strip() for i in text_widget.get("1.0", "end-1c").split("\n") if len(i.strip()) > 1]
    [print(f"{i + 1}. {elem}") for i, elem in enumerate(video_urls)]
    print()

    # Process each URL
    for url in video_urls:
        # Handle YouTube video URLs
        if "youtube.com/watch?v=" in url:
            yt = get_video_info(url)
            if not isinstance(yt, pytube.YouTube):
                print(f"Failed on {url} with status {yt}")
                continue

            # Download the video and audio
            highest_res_stream = yt.streams.get_highest_resolution()
            highest_res_stream.download(DIR)
            print(f"Video Downloaded in {highest_res_stream.resolution}")
            download_audio(yt)

        # Handle YouTube playlist URLs
        elif "youtube.com/playlist?list=" in url:
            extract_yt_playlist_links(url)

        # Handle other URLs
        else:
            download_webpage(url)


def download_audio(yt):
    # Get all audio streams and sort them by bitrate
    audio_streams = yt.streams.filter(only_audio=True)
    sorted_audio_streams = sorted(audio_streams, key=lambda s: int(s.bitrate), reverse=True)

    # Select the second best audio stream
    selected_audio_stream = sorted_audio_streams[1]

    # Get the video title
    video_title = yt.vid_info["videoDetails"]["title"]

    # Download the selected audio stream with the video title as filename
    selected_audio_stream.download(DIR, filename=f"{video_title}.mp3")

    # Print the audio download information
    print(f"Audio Downloaded in {selected_audio_stream.abr}")


def get_video_info(url):
    # Create YouTube object and get video info
    yt = pytube.YouTube(url=url)
    info = yt.vid_info
    status = info["playabilityStatus"]["status"]
    # json.dump(info, open(f"{DIR}/latest_video_info.json", "w"), indent=4) # debugging: save video info to file

    # Check video status
    if status not in ["PASS", "OK"]:
        return status

    # Print video details
    details = info['videoDetails']
    print(
        f"\"{details['title']}\" by {details['author']}, {format(int(details['viewCount']), ',d')} views, {details['lengthSeconds']}s, {yt.publish_date.strftime('%Y-%m-%d')}")

    return yt


def extract_yt_playlist_links(link):
    # Fetch and parse the webpage
    response = requests.get(link)
    parsed_response = BeautifulSoup(response.content, "html.parser").prettify()

    # Extract and load the YouTube data from the parsed response
    yt_data_str = next(
        line for line in parsed_response.replace('"', "`").split("\n") if "var ytInitialData = " in line)[23:-1]
    yt_data = json.loads(yt_data_str.replace("`", '"'))

    # Navigate through the nested structure of the YouTube data to get the video list
    video_list = yt_data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0]["tabRenderer"]["content"][
        "sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"][0]["playlistVideoListRenderer"][
        "contents"]

    # Extract video URLs and print them
    video_urls = []
    for video in video_list:
        title = video["playlistVideoRenderer"]["title"]["runs"][0]["text"]
        video_url = f'https://www.youtube.com/watch?v={video["playlistVideoRenderer"]["videoId"]}'
        video_urls.append(video_url)
        print(f"{title}, {video_url}")

    # Copy the video URLs to the clipboard
    pyperclip.copy("\n".join(video_urls))
    print(f"{len(video_urls)} YouTube links copied to clipboard")


def download_webpage(url):
    # Setup
    wkhtmltopdf_path = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    # Fetch webpage HTML and extract title
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else "webpage"
    # open(f'{DIR}/latest_webpage.html', 'w', encoding='utf-8').write(soup.prettify())

    # Sanitize title and create output path
    sanitized_title = "".join(c for c in title if c.isalpha() or c.isdigit() or c == ' ').rstrip()
    output_path = os.path.join(DIR, f"{sanitized_title}.pdf")

    # Save webpage as PDF
    try:
        pdfkit.from_url(url=url, output_path=output_path, configuration=config)
    except OSError as e:
        print(f"Failed to create PDF from {url}. Error: {e}")
    else:
        print(f"{url} saved as PDF with title: {sanitized_title}")


if __name__ == "__main__":
    # Setting up the root window
    root = tk.Tk()
    root.title("Web Content Downloader")
    root.geometry("600x300")
    root.config(bg="#1E1E1E")
    root.resizable(width=False, height=False)

    # Setting up labels
    tk.Label(root, text=" Web Content Downloader ", font="arial 20 bold", fg="#FFFFFF", bg="#464646").pack()
    tk.Label(root, text="Paste Link(s) Here:", font="arial 15 bold", fg="Black", bg="#EC7063").place(x=5, y=50)

    # Setting up text widget and scrollbar
    text_widget = tk.Text(root, height=10, width=70)
    text_widget.place(x=5, y=90)
    scrollbar = tk.Scrollbar(root, command=text_widget.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_widget.config(yscrollcommand=scrollbar.set)

    # Setting up buttons
    DIR = os.path.dirname(os.path.abspath(__file__))
    tk.Button(root, text="DOWNLOAD", font="arial 15 bold", fg="white", bg="#ff0000", padx=2,
              command=download_main).place(x=330, y=45)
    tk.Button(root, text="OPEN DIRECTORY", font="arial 8 bold", fg="white", bg="#ff0000", padx=2,
              command=lambda: subprocess.Popen(["explorer", DIR])).place(x=475, y=45, width=100)

    # Starting the main loop
    root.mainloop()
