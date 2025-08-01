# -*- coding: utf-8 -*-
"""youtube_page.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nzRvtXmVUV5J482_syRSRv6Gch8pb9w2
"""

import streamlit as st
import requests
from datetime import datetime, timedelta

# 👉 Your YouTube API Key
YOUTUBE_API_KEY = "AIzaSyBzXUdI5rPsBn6DeFiJE9IWgBfQc4dvpqU"  # replace with your API key

# App title
st.set_page_config(page_title="YouTube Influencer Finder", layout="wide")

# Add YouTube logo above the title
st.markdown("""
    <div style="text-align: center;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/0/09/YouTube_full-color_icon_%282017%29.svg" width="60">
    </div>
""", unsafe_allow_html=True)

st.title(" YouTube Influencer Finder")

# --- Styling to Match Your frontend.html ---
st.markdown("""
    <style>
    .influencer-card {
        background-color: #f9f9f9;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 12px;
        border: 1px solid #ddd;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
    }
    .influencer-card img {
        float: left;
        margin-right: 15px;
        border-radius: 50%;
    }
    .influencer-card:after {
        content: "";
        display: table;
        clear: both;
    }
    </style>
""", unsafe_allow_html=True)

# --- User Inputs ---
with st.sidebar:
    st.header("📋 Filters")
    country = st.text_input("Country", "India")
    industry = st.text_input("Industry", "Fashion")
    niche = st.text_input("Niche", "Streetwear")
    sub_min = st.number_input("Minimum Subscribers", min_value=0, value=1000, step=100)
    sub_max = st.number_input("Maximum Subscribers", min_value=0, value=100000, step=100)
    search = st.button("🚀 Search Influencers")

# --- Main Search Logic ---
def search_youtube_influencers(api_key, keyword, sub_min, sub_max, max_results=50, date_range_days=60):
    search_url = "https://www.googleapis.com/youtube/v3/search"
    video_url = "https://www.googleapis.com/youtube/v3/videos"
    channel_url = "https://www.googleapis.com/youtube/v3/channels"
    influencers = []
    added_channel_ids = set()

    today = datetime.utcnow()
    start_date = today - timedelta(days=date_range_days)
    start_date_str = start_date.isoformat("T") + "Z"

    search_params = {
        "part": "snippet",
        "q": keyword,
        "type": "video",
        "maxResults": max_results,
        "publishedAfter": start_date_str,
        "key": api_key
    }

    search_resp = requests.get(search_url, params=search_params).json()
    video_ids = [item["id"]["videoId"] for item in search_resp.get("items", [])]

    for video_id in video_ids:
        video_params = {
            "part": "snippet,statistics",
            "id": video_id,
            "key": api_key
        }
        video_resp = requests.get(video_url, params=video_params).json()
        if not video_resp.get("items"):
            continue

        video = video_resp["items"][0]
        views = int(video["statistics"].get("viewCount", 0))
        title = video["snippet"]["title"]
        channel_id = video["snippet"]["channelId"]
        channel_title = video["snippet"]["channelTitle"]

        if channel_id in added_channel_ids:
            continue

        channel_params = {
            "part": "snippet,statistics",
            "id": channel_id,
            "key": api_key
        }
        channel_resp = requests.get(channel_url, params=channel_params).json()
        if not channel_resp.get("items"):
            continue

        channel = channel_resp["items"][0]
        subs = int(channel["statistics"].get("subscriberCount", 0))
        total_views = int(channel["statistics"].get("viewCount", 0))
        profile_pic = channel["snippet"]["thumbnails"]["default"]["url"]
        trending_score = (views * 0.7) + (subs * 0.3)

        if sub_min <= subs <= sub_max:
            influencers.append({
                "name": channel_title,
                "profile_link": f"https://www.youtube.com/channel/{channel_id}",
                "subscribers": subs,
                "total_views": total_views,
                "top_video_title": title,
                "top_video_views": views,
                "top_video_link": f"https://www.youtube.com/watch?v={video_id}",
                "profile_pic": profile_pic,
                "trending_score": trending_score
            })
            added_channel_ids.add(channel_id)

    return influencers

# --- Run the Search ---
if search:
    with st.spinner("Searching for influencers..."):
        keyword = f"{country} {industry} {niche}"
        results = search_youtube_influencers(YOUTUBE_API_KEY, keyword, sub_min, sub_max)

        if results:
            for inf in results:
                st.markdown(f"""
                    <div class="influencer-card">
                        <img src="{inf['profile_pic']}" width="60">
                        <strong>{inf['name']}</strong><br>
                        <a href="{inf['profile_link']}" target="_blank">YouTube Profile</a><br>
                        📺 Subscribers: {inf['subscribers']}<br>
                        👁️ Total Views: {inf['total_views']}<br>
                        🔥 Trending Score: {int(inf['trending_score'])}<br>
                        🎬 <a href="{inf['top_video_link']}" target="_blank">{inf['top_video_title']}</a><br>
                        📈 Top Video Views: {inf['top_video_views']}
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("No influencers found in that range. Try adjusting the filters!")