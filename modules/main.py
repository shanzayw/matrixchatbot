import asyncio
import time
import sys
import hashlib
import uuid
import ci_stats

sys.path.append("./../")    #allows python interpreter to find modules

from nio import (AsyncClient, AsyncClientConfig, RoomMessageText,
    InviteEvent, RoomMessageImage, RoomMessageMedia, RoomEncryptionEvent)
from models.database import create_tables
from services.database_service import (check_if_room_is_existing,
    check_if_user_is_existing, create_new_room, create_new_user,
    create_new_message, get_number_of_links_to_be_shown, get_salt_value,
    add_salt_value, check_if_room_is_existing, get_all_domains_original,
    get_room_ids)
from nlp import language_processing
from message_evaluation import evaluate_message
from response_management import generate_response
from config import Config

#set filepath of config file
config_filepath = "../config.yaml"
config = Config(config_filepath)

#AsyncClient configuration options
client_config = AsyncClientConfig(
    store_sync_tokens=True,
    encryption_enabled=False,
)

#initialize matrix client
client = AsyncClient(
    config.homeserver_url,
    config.user_id,
    config=client_config,
)

'''
The main module controls the processing of events via callback functions
1) InviteEvents --> auto-join room
2) MessageEvents --> pass message to other modules

The module also sends messages to the matrix homeserver
'''

async def main():

    #client login
    await client.login(password=config.user_password)
    print("login successful")

    #add event callbacks
    client.add_event_callback(message_cb, RoomMessageText)
    client.add_event_callback(auto_join_room_cb, InviteEvent)

    #sync encryption keys (encrypted rooms currently not working))
    if client.should_upload_keys:
        await client.keys_upload()

    await client.sync_forever(timeout=30000, full_state=True)

    #close client connection on disconnect
    await client.close()

async def sendMessage(room_id, response):
    '''send messages to room via room id'''

    await client.room_send(
        room_id=room_id,
        message_type="m.room.message",
        content={
            "msgtype": "m.text",
            "body": str(response)
        }
    )

async def message_cb(room, event):
    '''called whenever a new message event has been detected'''

    room_id = str(room.room_id)
    user_name = room.user_name(event.sender)

    #ignore own messages
    if event.sender == client.user:
        return

    else:

        #hasing of the user name with salt
        salt_value = get_salt_value()
        salt_value = salt_value[0]
        salt_value = salt_value.encode('utf-8')
        user_name = user_name.encode('utf-8')
        hashed_user_name = hashlib.sha512(user_name + salt_value).hexdigest()
        user_name = hashed_user_name

        message_body = event.body

        event_timestamp = event.server_timestamp #tiestamp in ms (unix time)
        current_timestamp = int(round(time.time() * 1000))
        timestamp_difference = current_timestamp - event_timestamp

        if timestamp_difference < 20000:   #ignore old messages

            print("New message event: " + str(message_body))
            if check_if_user_is_existing(user_name) == False:
                #create new user entry in db
                create_new_user(user_name, "general") #add name of inserted module

            #pass message to other modules
            processed_message = language_processing(message_body)
            evaluation = evaluate_message(user_name, processed_message)
            response = generate_response(user_name, evaluation, message_body)

            if response != "":
                #send response
                print("New response: " + str(response))
                await sendMessage(room_id, response)

#auto join rooms
async def auto_join_room_cb(room, event):
    '''called when the chatbot received a new room invite'''

    room_id = room.room_id
    user_name = room.user_name(event.sender)
    if user_name == None:
        return
    salt_value = get_salt_value()
    if salt_value == None:
        salt_value = uuid.uuid4().hex
        add_salt_value(salt_value)
    salt_value = salt_value[0]
    salt_value = salt_value.encode('utf-8')
    user_name = user_name.encode('utf-8')
    hashed_user_name = hashlib.sha512(user_name + salt_value).hexdigest()
    user_name = hashed_user_name

    #create new user, room entry in db if not already existing
    if check_if_user_is_existing(user_name) == False:
        create_new_user(hashed_user_name, "general") #add name of inserted module

    if check_if_room_is_existing(room_id) == False:
        create_new_room(room_id, hashed_user_name)
        await client.join(room_id)
        print("Joined a new room.")

        all_modules = get_all_domains_original()
        string_with_modules = ""
        for i in range(0, len(all_modules)):
            current = all_modules[i][0]
            if current != "General":
                if string_with_modules == "":
                    string_with_modules = string_with_modules + current
                else:
                    string_with_modules = string_with_modules + ", " + current

        standard_first_message = "Hi, I'm your chatbot helping you with"\
            " whatever you need! Call 'help' to see all my options. I've"\
            " information about the following modules: " + string_with_modules

        await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content = {
                "msgtype": "m.text",
                "body": standard_first_message
            }
        )

asyncio.get_event_loop().run_until_complete(main())
