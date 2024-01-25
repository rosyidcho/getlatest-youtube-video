import sys
import os.path
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import time
from reprint import output

'''
Python script to get the latest 3 YouTube videos from specified channels.

Creator: rosyidcho

version: 0.02
'''

def calPB(iTMPCount, iTMPMAX):
    tmpCalPB = ''
    current_progress = int(iTMPCount)
    true_length = int(current_progress/iTMPMAX*100)
    true_length = int(true_length/10)
    tmpCalPB = '[{done}{padding}] {percent}%'.format(
                                            done = "#" * int(true_length*2),
                                            padding = " " * (20 - int(true_length*2)),
                                            percent = int(true_length*10)
    )
    return tmpCalPB

def get_last_3_videos(List_File):
    # Read channel URLs from a file
    print(f'[+] Loading youtube channel list')
    with open(List_File, "r") as file:
        channel_urls = [line.strip() for line in file.readlines()]

    all_videos_info = []
    
    imaxURL = len(channel_urls)
    iURL = 0
    with output(initial_len=6, interval=0) as output_lines:
        for channel_url in channel_urls:
            iURL += 1
            output_lines[0] = f'[+] Getting channel no. {iURL}'
            output_lines[1] = f'    Progress : {calPB(iURL, imaxURL)}'
            url = f"{channel_url}/videos"
            headers = {
                "Accept-Language": "en-US,en;q=0.5",  # Adjust the language preference as needed
            }
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")
            output_lines[2] = f'[+] Accessing the channel page {channel_url}...'

            # Extract the JSON data embedded in the HTML response
            scripts = soup.find_all("script")
            videos_info = []
            for script in scripts:
                if "var ytInitialData" in str(script):
                    output_lines[3] = f'[+] Getting the latest videos...'
                    json_data = script.string.split(" = ")[1]
                    json_data = json_data[:json_data.rfind(";")]
                    data = json.loads(json_data)

                    sections = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][1]['tabRenderer']['content']['richGridRenderer']['contents']
                    iLoop = 0
                    for section in sections:
                        if 'richItemRenderer' in section:
                            iLoop += 1
                            output_lines[4] = f'[+] Getting video no.{iLoop}'
                            output_lines[5] = f'    Progress : {calPB(iLoop, 3)}'
                            # Give delay if it's to fast
                            time.sleep(0.3)
                            videos = section['richItemRenderer']['content']['videoRenderer']
                            video_data = {
                                "Video URL": f"https://www.youtube.com/watch?v={videos['videoId']}",
                                "Title": videos['title']['runs'][0]['text'],
                                "Channel Name": channel_url.split('/')[-1],
                                "View Count": videos['viewCountText']['simpleText'],
                                "Publish Date": videos['publishedTimeText']['simpleText']
                            }
                            videos_info.append(video_data)

                        # Limit to 3 latest videos
                        if iLoop == 3: break

            # return videos_info
            all_videos_info.extend(videos_info)
    
    if all_videos_info:
        now = datetime.now()
        now = now.strftime("%Y-%m-%d_%H-%M-%S")
        output_file = f"output_{now}.xlsx"
        df = pd.DataFrame(all_videos_info)
        df.to_excel(output_file, index=False)
        print(f"[+] Data exported to {output_file}")
    else:
        print(f"[!] No Data to be exported")

if __name__ == "__main__":
    # Check if list file is selected
    if len(sys.argv) != 2:
        print('\n[!] Choose a file that contain list of channel(s)')
        print(f'[!] Use command like this: python \x1B[3m{os.path.basename(__file__)} list_yt_channel_file\x1B[0m\n')
        sys.exit(4)
    if not os.path.isfile(sys.argv[1]):
        print('[!] Choose a file...!!!')
        sys.exit(4)
    else:
        list_file = sys.argv[1]

    print("[+] This script version is 0.02")
    get_last_3_videos(list_file)