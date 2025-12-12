from youtubesearchpython import VideosSearch

def get_yt_video(query):
    videos_search = VideosSearch(query, limit=3)
    result = videos_search.result()
    if result['result']:
        video_titles = [video['title'] for video in result['result']]
        video_links = [video['link'] for video in result['result']]
        return video_titles, video_links

    return [], []