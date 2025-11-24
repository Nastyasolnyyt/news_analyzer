from telethon.sync import TelegramClient
import csv
import datetime

api_id = 34045959
api_hash = 'b126e73a8a872a5d03704d8f4f777078'
phone = '+79196510789'

channels = ['https://t.me/rbc_news', 'https://t.me/mash']

output_file = 'news_data.csv'

print("Parser is starting")

session = 'mfin'

client = TelegramClient(session,api_id,api_hash )
client.start()

print("connected to telegram!")

with open(output_file,'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Channel', 'Date', 'Text news', 'link'])

    for channel in channels:
        print(f"Downloading news {channel}")
        try:
            posts = client.get_messages(channel, limit =100)
            for post in posts:
                if post.text:
                    writer.writerow([channel, post.date, post.text, f"https://t.me/rbc_news/{post.id}"])
        except Exception as e:
                peint(f"Error reading channel")

print("Ready! Data in news_data.csv")

