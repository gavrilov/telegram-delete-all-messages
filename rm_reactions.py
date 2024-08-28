import os
import argparse

from telethon.sync import TelegramClient
from telethon.tl.types import Channel, Chat, PeerUser

from pyrogram.client import Client


API_ID = os.getenv('API_ID', None) or int(input('Enter your Telegram API id: '))
API_HASH = os.getenv('API_HASH', None) or input('Enter your Telegram API hash: ')

# telethon and pyrogram have different session file formats - because of this the script created 2 sessions and you had to log in twice
session_name_pyrogram ='rm_reactions_pyrogram'
session_name_telethon = 'rm_reactions_telethon'
client = TelegramClient(session_name_telethon, API_ID, API_HASH)
app = Client(session_name_pyrogram, api_id=API_ID, api_hash=API_HASH)

async def rm_reaction(app, chat_id, msg_id):
    try:
        await app.send_reaction(chat_id, msg_id)
    except Exception as e:
        print("Failed to remove reaction:", e)

async def main():
    async with app:
        parser = argparse.ArgumentParser(description="Process some flags.")
        parser.add_argument('-l', '--list', action='store_true', help='list chats with reactions but do not delete')

        args = parser.parse_args()

        me = await client.get_me()
        # print(f"me.id: {me.id}")

        dialogs = await client.get_dialogs()
        groups = []
        
        for dialog in dialogs:
            entity = dialog.entity
            if isinstance(entity, Chat) or (isinstance(entity, Channel) and entity.megagroup):
                groups.append(dialog)

        if not groups:
            print("No groups found.")
            return

        print(f"Available groups({len(groups)}):")
        for i, group in enumerate(groups):
            print(f"{i}. {group.name}")
        print(f"{len(groups)}. ALL GROUPS")

        selected_group_indexs = input("Select one or many groups by entering their indexes comma separated: ")

        str_list = selected_group_indexs.split(',')
        int_list = [int(num.strip()) for num in str_list]

        groups_to_process = []
        if len(int_list) == 1 and selected_group_indexs[0] == len(groups):
            groups_to_process = groups
        else:
            for i in int_list:
                groups_to_process.append(groups[i])

        print(f"\nGroups to Process:")
        for g in groups_to_process:
            print(f"\t{g.name}")


        for g in groups_to_process:
            print(f"\nProcessing {g.name}")
            count = await rm_reactions_from_chat(app, g.id, me, not args.list)
            if args.list:
                print(f"{g.name} has {count} reactions")
            else:
                print(f"Removed {count} reactions from {g.name}")


async def rm_reactions_from_chat(app, chat_id, me, rm: bool = False):
    reactionCount = 0
    numMessages = await app.get_chat_history_count(chat_id)
    i = 0
    async for message in client.iter_messages(chat_id):
        print(f"Progress: {i + 1}/{numMessages} ({(i + 1) / numMessages * 100:.2f}%)", end='\r')
        if message.reactions:
            # print(f'message.reactions: {message.reactions}')
            recent_reactions = message.reactions.recent_reactions
            if recent_reactions == None:
                continue
            for reaction in recent_reactions:
                user = reaction.peer_id
                # print(f"comparing me.id: {me.id} and user: {user}")
                if isinstance(user, PeerUser) and me.id == user.user_id:
                    # print(f"User {user} reacted with {reaction.reaction} to post message_id: {message.id}: {message.text}.")
                    if rm:
                        await rm_reaction(app, chat_id, message.id)
                        print(f"Removed reaction on msg_id: {message.id}")
                    reactionCount+=1
        i += 1
    return reactionCount

with client:
    client.loop.run_until_complete(main())
