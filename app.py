import os
import pandas as pd
import re
import random
import telebot
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

BOT_TOKEN = "6281262156:AAE5SJNwdj0ZTT1lu-SymsnxFpRoUxrRANo"
SPOTIPY_CLIENT_ID = "00f3cc41c1d042a29eec6d232b45582d"
SPOTIPY_CLIENT_SECRET = "93a1d380a7ae483699feb6d7b8d31e74"


bot = telebot.TeleBot(BOT_TOKEN)

df = pd.read_csv("merged.csv")
options = list(df["album"].unique())
era_options = [var.split(" (")[0] for var in options]

regex = r"\s"

# use the regular expression to split each string into words
words = df["name"].str.split(regex)


# define a lambda function to capitalize each word that does not follow an apostrophe
def capitalize(word):
    if re.match(r"^[a-z][a-z']+$", word):
        return word.capitalize()
    else:
        return word


# apply the lambda function to each word
words_capitalized = words.apply(lambda lst: [capitalize(word) for word in lst])

# combine the words back into strings
df["name"] = words_capitalized.str.join(" ")
songs = list(df["name"])


# Set up authentication with Spotify API
client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def search_song(query):
    results = sp.search(q=query, type="track")
    if results["tracks"]["items"]:
        return results["tracks"]["items"][0]["external_urls"]["spotify"]
    else:
        return None


@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):
    bot.reply_to(
        message,
        "Type /random to get recommended a Taylor Swift song!\nType /eras to choose what Taylor Swift era you want to dress up as and the bot will select one for you!",
    )


@bot.message_handler(commands=["random"])
def send_recommendation(message):
    song = random.choice(songs)
    album = df.loc[df["name"] == song, "album"].reset_index()["album"][0]
    album = album.split(" (")[0]
    print(song)
    song_link = search_song(song + " Taylor Swift")
    if song_link:
        print(song_link)
    else:
        print("Song not found")
        song_link = "Song not found on Spotify"
    bot.reply_to(
        message, "{} from {}. Listen to the song at {}".format(song, album, song_link)
    )


@bot.message_handler(commands=["eras"])
def eras_command_handler(message):
    # Create the poll with multiple selections
    poll = bot.send_poll(
        message.chat.id,
        "Choose the eras that you're thinking of dressing up as:",
        era_options,
        is_anonymous=False,
        allows_multiple_answers=True,
    )


# Get the results of the poll
@bot.poll_answer_handler()
def handle_poll_answer(pollAnswer):
    eras = []
    for option in pollAnswer.option_ids:
        eras.append(era_options[option])

    # Randomly select one of the options
    selected_option = random.choice(eras)
    print(selected_option)
    title = selected_option.lower().replace(" ", "_")

    # Send a message with the option text
    bot.send_message(
        pollAnswer.user.id,
        "You should dress up as Taylor from <b>{}</b>! Here is an idea... #eras".format(
            selected_option
        ),
        parse_mode="HTML",
    )
    with open("{}.png".format(title), "rb") as image_file:
        # Send the photo to the chat
        bot.send_photo(pollAnswer.user.id, image_file)


bot.polling()
