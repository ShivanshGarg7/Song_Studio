import streamlit as st
import pickle
import pandas as pd
from dotenv import load_dotenv
import json  
import os
import base64
from requests import post, get

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

# For Spotify Token
def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
    url = "https://accounts.spotify.com/api/token"

    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}



def song_recommendation(song_name):
    song_index = songs_list[songs_list['name'] == song_name].index[0]
    gapping = similar[song_index]
    songs_listing = sorted(list(enumerate(gapping)),reverse=True, key=lambda x:x[1])[1:11]
    
    recommended_song = []
    for i in songs_listing:
        recommended_song.append(songs_list['name'].iloc[i[0]])
    return recommended_song


songs_list_dict = pickle.load(open('song_list_dict.pkl', 'rb'))
songs_list = pd.DataFrame(songs_list_dict)
artist_list = pickle.load(open('latest_artist.pkl', 'rb'))

similar = pickle.load(open('similar.pkl', 'rb'))

st.set_page_config(page_title="Song Studio", layout="wide")

st.markdown(
    "<h1>Song Studio </h1>",
    unsafe_allow_html=True,
)

st.markdown(
    """
    <p>Welcome to <b>Song Studio</b>, a Music recommendation system designed to suggest songs and artists based on your preferences.</p>
    <p>Developed with ❤️ to make your Music discovery fun and seamless!</p>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr>", unsafe_allow_html=True)



st.subheader("Artist Recommendation:")
artist_name_selection = st.selectbox(
        "Select a Artist", artist_list
    )


def artist_search(token, artist_name):
        url =  f"https://api.spotify.com/v1/search"
        headers = get_auth_header(token)
        query = f"?q={artist_name}&type=artist&limit=1"
        query_url = url + query
        result = get(query_url, headers=headers)
        json_result = json.loads(result.content)["artists"]["items"]
        if len(json_result) == 0:
            print("No Artist Found....")
            return None
        return json_result[0]



def get_songs_by_artist(token, artist_id):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
        headers = get_auth_header(token)
        result = get(url, headers=headers)
        json_result = result.json()
        tracks_info = []
        for track in json_result['tracks']:
            track_name = track['name']
            track_image = track['album']['images'][0]['url']
            spotify_url= track['external_urls']['spotify']
            tracks_info.append({
                'name': track_name,
              'image_url': track_image,
              'spotify_url': spotify_url
        })
        return tracks_info



token = get_token()
    
result = artist_search(token, artist_name_selection)
artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)


if st.button("Get Artist Recommendation:"):
        st.write("Here are some Recommendation:")
        num_columns = 4
        cols = st.columns(num_columns)
        for idx, song in enumerate(songs):
            with cols[idx % num_columns]:
                st.image(song['image_url'], width=500)
                st.markdown(f"<p style='text-align:center; font-size:18px'><a href='{song['spotify_url']}' target='_blank' style='text-decoration:none; color: inherit'><b>{song['name']}</b></p>", unsafe_allow_html=True)


st.subheader("Song Recommendation:")
song_name_selection = st.selectbox(
        "Select a Song", songs_list['name'].values
    )
if st.button('Get Recommendation Songs'):
        recommended_songs = song_recommendation(song_name_selection)
        st.write("Here are some Recommendation:")
        for i in recommended_songs:
            st.write("*", i)


st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)




st.subheader("👩‍💻 About the Developer")
st.write(
    """
    Hey! My name is **Shivansh Garg**, and I created this app to combine my love for Music and Programming. 
    This app leverages recommendation Algorithms to give you personalized song and artist suggestions with Spotify API Integration.

    
    - Connect with me: [LinkedIn](https://www.linkedin.com/in/shivansh-garg-584625221/) | [GitHub](https://github.com/ShivanshGarg7)
    """
)






