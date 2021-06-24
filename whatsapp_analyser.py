#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import re
from nltk import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
import datetime


def make_dataframe(): # Function to make an empty data frame
    global df # Make global variable
    df = pd.DataFrame(columns=['Date',"Name","Message"]) # Assign empty pandas data frame to df
    
make_dataframe() # Run function


def make_message_list(filename): # Function to make list of messages from whatsapp.txt file

    f = open(filename, 'r') # open file
    
    global messages # global variable for messages
    
    messages = f.readlines() # read .txt file in lines into messages variabls
    
make_message_list("") # Run function on text file - pass whatsapp.txt filename as a string into this function



def dates_to_dataframe(df,messages): # Function to get dates from messages and add to dataframe
    
    date_regex = "[0-9]{2}/[0-9]{2}/[0-9]{4}" # regex for dd/mm/yyyy
    
    dates_list = [] # Empty list to store date for each message(local)
    
    for message in messages: # Iterate messages
        
        if re.search(date_regex,message): # If Regex search is True
            dates_list.append(re.search(date_regex,message).group()) # Append the matched search
        else:
            dates_list.append("N/A") # Else Append N/A (Handling for spotify song sharing which counts as own message)
      
    df["Date"] = dates_list # Add dates list to df
        
dates_to_dataframe(df,messages) # Run Function



def names_to_dataframe(df,messages): # Function to get name of messager from messages and add to data frame
    
    name_regex = "[A-Z]{1}[a-z]+ [A-Z]{1}[a-z]+" # Regex for First Name followed by second name (capitilized)
    
    names_list = [] # Empty list for names
    
    for message in messages: # Iterate through messages
        
        if re.search(name_regex, message): # If regex search is True
            names_list.append(re.search(name_regex, message).group())  # Append the matched search to time list
        else:
            names_list.append("N/A") # Else Append N/a (Handling for spotify song sharing)
            
    df["Name"] = names_list # Add names list to df

names_to_dataframe(df,messages) # Run Function


def message_to_dataframe(df,messages):
    
    end_of_name_regex = "[A-Z]{1}[a-z]+ [A-Z]{1}[a-z]+: " # Regex for name and colon (i.e end span == message start)
    
    message_list = [] # Empty List for processed messages

    for message in messages: # Iterate message list
    
        if re.search(end_of_name_regex, message): # If regex search is True
            
            message_start_index = re.search(end_of_name_regex, message).span()[1] # Create index number from end of regex name check
            
            message_list.append(message[message_start_index:-1]) # Append message from index onwards (excluding last character which is \n)
        else:
            message_list.append(message) # Else append full message (spotify handling)
            
    df["Message"] = message_list # Add Message to df

message_to_dataframe(df,messages) # Run Function


def split_per_person(df): # Function to create two data frames, one for each person

    person_1 = df["Name"].iloc[0] # Set string variable as the name of the person to first send a message
    
    df_person1 = df[df['Name'].str.contains(person_1)] # Subset by rows that contain person_1 string
    df_person2 = df[~df['Name'].str.contains(person_1)] # Subset by rows that DO NOT contain person_1 string

    return df_person1, df_person2

df_person1, df_person2 = split_per_person(df) # Run Function



"""Data Analysis from messages - Word Clouds and Time Series (Rolling Average)"""


def top_words_wordcloud(df): # Create lists and word:wordcount dictionary for analysis - inc. wordclouds
    
    sw = stopwords.words('english') # Create stopwords list
    punc = list(punctuation) # Create Punctuation list

    word_list = [] # Empty list to store all words
    
    for message in df["Message"]: # Iterate messages
        words = word_tokenize(message.lower()) # Tokenize and lower case into list of words per message
        for word in words: # Iterate words in message
            if word not in sw and word not in punc: # If not a stop word or punctuation:
                word_list.append(word) # Add to word list
    
    unique_word_list = list(set(word_list)) # Create iterable list of unique words
    
    word_count_dictionary = {word:word_list.count(word) for word in unique_word_list} # word:wordcount dictionary
    
    wc = WordCloud(height = 1000, width = 1500, background_color ='white', min_font_size = 2) # Generate Cloud

    wc.generate_from_frequencies(frequencies=word_count_dictionary) # Size based on frequency from dictionary

    plt.figure() #Use Matplot Lib to Display
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()


top_words_wordcloud(df_person1) # Run Function for person 1
top_words_wordcloud(df_person2) # Run Function for person 2

"""Time Series"""

df['Date'] = pd.to_datetime(df['Date'], errors = 'coerce', format='%d/%m/%Y', dayfirst = True) # Turn Date to DateTime Format

df = df.dropna() # Drop any N/A i.e spotify

df.index = pd.DatetimeIndex(df["Date"]) # Set Index to Date

df = df.drop(columns = ["Date"]) # Remove Date Column as date as index exists

df_plot = pd.DataFrame(columns=['Count',"Rolling Avg"]) # Create New data Frame with Columns for message count per day and rolling avg

df_plot["Count"] = df["Message"].groupby(df.index.date).count() # Count messages per day by date index

df_plot["Rolling Avg"] = df_plot.Count.rolling(7).mean().shift(-3) # Calculate rolling 7-day average

start = pd.to_datetime("2019-10-25").date() # Create start date and create end date for specific date range
end = pd.to_datetime("2019-10-30").date()

df_plot.loc[start:end] # Subset Data frame by start and end date

fig, ax = plt.subplots(figsize=(18, 8)) # Create fig, ax

df_test["Rolling Avg"].plot(ax=ax) # Plot rolling average

style = dict(size=10, color='gray') # Style

"""Mean and Max sent messages"""

def mean_max(df): # Function to return the mean and max messages sent from a day
    
    mean_sent = df["Count"].mean()
    max_sent = df["Count"].max()
    
    print (f"In the last year, we have averaged {mean_sent} messages a day, and the most sent in one day was {max_sent}")

mean_max(df_plot) 

