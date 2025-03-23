import os
try:
    import threading
    import requests
    import telebot
    from telebot import types
    from api import braintree_auth
    import time
except:
    os.system('pip install requests fake_useragent bs4 telebot ')
# Bot configuration
TOKEN = "7901171759:AAFPdDsnGxuRv-iNg8kyDIVP1NCMl1NrwR0"  # Replace with your bot token
OWNER_ID = 7465126380 # Replace with your owner ID

# Initialize the bot
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# File paths
APPROVED_USERS_FILE = "approved_users.txt"

# Global state
processing = {}
stop_processing = {}
approved_users = set()

def remove(filename: str, delete_line: str) -> None:
        with open(filename, "r+") as io:
            content = io.readlines()
            io.seek(0)
            for line in content:
                if not (delete_line in line):
                    io.write(line)
            io.truncate()

# Load approved users from file
def load_approved_users():
    try:
        with open(APPROVED_USERS_FILE, "r") as file:
            return set(line.strip() for line in file.readlines())
    except FileNotFoundError:
        return set()

# Save approved user to file
def add_approved_user(user_id):
    with open(APPROVED_USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")

# Ban a user
def ban_user(user_id):
    remove("approved_users.txt", user_id)

# Generate approved card message
def generate_approved_message(cc, response, bin_info, time_taken):
    return f"""
𝘼𝙥𝙥𝙧𝙤𝙫𝙚𝙙 ✅
                
𝘾𝙖𝙧𝙙 ➼ <code>{cc}</code>

𝙍𝙚𝙨𝙥𝙤𝙣𝙨𝙚 ➼ {response}
𝙂𝙖𝙩𝙚𝙬𝙖𝙮 ➼ ⤿ Braintree Auth ⤾        
𝙄𝙣𝙛𝙤 ➼ {bin_info.get('type', 'Unknown')} - {bin_info.get('brand', 'Unknown')} - {bin_info.get('level', 'Unknown')}
𝘾𝙤𝙪𝙣𝙩𝙧𝙮 ➼ {bin_info.get('country_name', 'Unknown')} - {bin_info.get('country_flag', '')}
𝙄𝙨𝙨𝙪𝙚𝙧 ➼ {bin_info.get('bank', 'Unknown')}
𝘽𝙞𝙣 ➼ {cc[:6]}
𝙏𝙞𝙢𝙚 ➼ {time_taken}
𝗕𝗼𝘁 𝗕𝘆: @HARISH_GAMER1
"""

# Handle /start command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = str(message.from_user.id)
    if user_id not in load_approved_users():
        bot.reply_to(message, "𝘠𝘰𝘶 𝘢𝘳𝘦 𝘯𝘰𝘵 𝘢𝘱𝘱𝘳𝘰𝘷𝘦𝘥 𝘵𝘰 𝘶𝘴𝘦 𝘵𝘩𝘪𝘴 𝘣𝘰𝘵. 𝘊𝘰𝘯𝘵𝘢𝘤𝘵 𝘵𝘩𝘦 𝘰𝘸𝘯𝘦𝘳- @HARISH_GAMER1")
        return
    bot.reply_to(message, "𝗦𝗲𝗻𝗱 𝗧𝗵𝗲 𝗙𝗶𝗹𝗲 𝗧𝗼 𝗖𝗵𝗲𝗰𝗸 ✔️")

# Handle /add command (owner only)
@bot.message_handler(commands=["add"])
def add_user(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "𝗙𝘂𝗰𝗸 𝗬𝗼𝘂 𝗞𝗶𝗱💀")
        return
    try:
        user_id_to_add = message.text.split()[1]
        add_approved_user(user_id_to_add)
        approved_users.add(user_id_to_add)
        bot.reply_to(message, f"𝗨𝘀𝗲𝗿 {user_id_to_add} 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝐚𝐩𝐩𝐫𝐨𝐯𝐞𝐝.")
    except IndexError:
        bot.reply_to(message, "𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘂𝘀𝗲𝗿 𝗜𝗗 𝗧𝗼 𝗮𝗽𝗽𝗿𝗼𝘃𝗲.")

# Handle /ban command (owner only)
@bot.message_handler(commands=["remove"])
def ban_user_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "𝗙𝘂𝗰𝗸 𝗬𝗼𝘂 𝗞𝗶𝗱💀")
        return
    try:
        user_id_to_ban = message.text.split()[1]
        ban_user(user_id_to_ban)
        bot.reply_to(message, f"𝗨𝘀𝗲𝗿 {user_id_to_ban} 𝐡𝐚𝐬 𝐛𝐞𝐞𝐧 𝗕𝗮𝗻𝗻𝗲𝗱.")
    except IndexError:
        bot.reply_to(message, "𝗣𝗿𝗼𝘃𝗶𝗱𝗲 𝗮 𝘂𝘀𝗲𝗿 𝗜𝗗 𝘁𝗼 𝗯𝗮𝗻..")

# Handle document upload
@bot.message_handler(content_types=["document"])
def handle_document(message):
    user_id = str(message.from_user.id)
    if user_id not in load_approved_users():
        bot.reply_to(message, "𝘊𝘰𝘯𝘵𝘢𝘤𝘵 𝘵𝘩𝘦 𝘰𝘸𝘯𝘦𝘳- @HARISH_GAMER1")
        return

    if processing.get(user_id, False):
        bot.reply_to(message, "𝗣𝗹𝗲𝗮𝘀𝗲 𝘄𝗮𝗶𝘁! 𝗬𝗼𝘂𝗿 𝗽𝗿𝗲𝘃𝗶𝗼𝘂𝘀 𝗳𝗶𝗹𝗲 𝗶𝘀 𝘀𝘁𝗶𝗹𝗹 𝗯𝗲𝗶𝗻𝗴 𝗽𝗿𝗼𝗰𝗲𝘀𝘀𝗲𝗱. ⏳.")
        return

    processing[user_id] = True
    stop_processing[user_id] = False

    # Download the file
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_path = f"combo_{user_id}.txt"
    with open(file_path, "wb") as file:
        file.write(downloaded_file)

    # Start processing
    ko = bot.reply_to(message, "𝘊𝘰𝘯𝘯𝘦𝘤𝘵𝘪𝘯𝘨 𝘕𝘦𝘵𝘸𝘰𝘳𝘬 𝘛𝘰 𝘊𝘩𝘦𝘤𝘬 𝘊𝘢𝘳𝘥𝘴.....⏳.").message_id
    threading.Thread(target=process_cards, args=(message, file_path, user_id, ko)).start()

# Process cards
def process_cards(message, file_path, user_id, ko):
    dd = 0
    ch = 0
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            total = len(lines)

            for cc in lines:
                if stop_processing.get(user_id, False):
                    bot.send_message(message.chat.id, "🛑 𝙋𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝘀𝙩𝙤𝙥𝙥𝙚𝙙 𝙗𝙮 𝙪𝙨𝙚𝙧.")
                    break

                cc = cc.strip()
                # Perform BIN lookup
                bin_info = {}
                try:
                    bin_data_url = f"https://bins.antipublic.cc/bins/{cc[:6]}"
                    bin_info = requests.get(bin_data_url).json()
                except Exception as e:
                    print(f"BIN Lookup Error: {e}")

                # Inline keyboard with Stop button
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• ➼ {cc} •", callback_data='u8')
                cm2 = types.InlineKeyboardButton(f"• 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅: [ {ch} ] •", callback_data='x')
                cm3 = types.InlineKeyboardButton(f"• 𝗗𝗲𝗮𝗱 ❌: [ {dd} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• 𝗧𝗼𝘁𝗮𝗹 💎: [ {total} ] •", callback_data='x')
                mes.add(cm1, cm2, cm3, cm4)

                bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝘾𝘼𝙍𝘿𝙎...''', reply_markup=mes)

                # Process card using Tele function
                try:
                    last = str(braintree_auth(cc))  # Use the Tele function from gatet.py
                except Exception as e:
                    print(e)
                    

                # Update counts based on response
                if "Approved ✅" in last:
                    ch += 1
                    approved_message = generate_approved_message(cc, "Approved", bin_info, "4.6")
                    bot.send_message(message.chat.id, approved_message)  # Send to user's DM
                else:
                    dd += 1

                # Update the portal with current counts
                mes = types.InlineKeyboardMarkup(row_width=1)
                cm1 = types.InlineKeyboardButton(f"• ➼ {cc} •", callback_data='u8')
                cm2 = types.InlineKeyboardButton(f"• 𝗔𝗽𝗽𝗿𝗼𝘃𝗲𝗱 ✅: [ {ch} ] •", callback_data='x')
                cm = types.InlineKeyboardButton(f"• ➼ {last} •", callback_data='u8')
                cm3 = types.InlineKeyboardButton(f"• 𝗗𝗲𝗮𝗱 ❌: [ {dd} ] •", callback_data='x')
                cm4 = types.InlineKeyboardButton(f"• 𝗧𝗼𝘁𝗮𝗹 💎: [ {total} ] •", callback_data='x')
                mes.add(cm1, cm, cm2, cm3, cm4)

                bot.edit_message_text(chat_id=message.chat.id, message_id=ko, text='''𝘾𝙃𝙀𝘾𝙆𝙄𝙉𝙂 𝙔𝙊𝙐𝙍 𝘾𝘼𝙍𝘿𝙎...''', reply_markup=mes)

    except Exception as e:
        print(f"Error processing cards: {e}")
    finally:
        processing[user_id] = False
        stop_processing[user_id] = False
        bot.send_message(message.chat.id, "✅ 𝘾𝙝𝙚𝙘𝙠𝙞𝙣𝙜 𝙘𝙤𝙢𝙥𝙡𝙚𝙩𝙚! 𝙔𝙤𝙪 𝙘𝙖𝙣 𝙣𝙤𝙬 𝙨𝙚𝙣𝙙 𝙖 𝙣𝙚𝙬 𝙛𝙞𝙡𝙚.")

# Handle stop button
@bot.message_handler(commands=["stop"])
def stop_processing_callback(call):
    user_id = str(call.from_user.id)
    if user_id in processing and processing[user_id]:
        stop_processing[user_id] = True
        bot.answer_callback_query(call.id, "Processing has been stopped.")
    else:
        bot.answer_callback_query(call.id, "No ongoing processing to stop.")

# Handle /status command
@bot.message_handler(commands=["status"])
def status(message):
    user_id = str(message.from_user.id)
    if user_id in processing and processing[user_id]:
        bot.reply_to(message, "𝙔𝙤𝙪𝙧 𝙛𝙞𝙡𝙚 𝙞𝙨 𝙨𝙩𝙞𝙡𝙡 𝙗𝙚𝙞𝙣𝙜 𝙥𝙧𝙤𝙘𝙚𝙨𝙨𝙚𝙙. 𝙋𝙡𝙚𝙖𝙨𝙚 𝙬𝙖𝙞𝙩.")
    else:
        bot.reply_to(message, "𝙉𝙤 𝙛𝙞𝙡𝙚 𝙥𝙧𝙤𝙘𝙚𝙨𝙨𝙞𝙣𝙜 𝙞𝙣 𝙥𝙧𝙤𝙜𝙧𝙚𝙨𝙨 𝙖𝙩 𝙩𝙝𝙚 𝙢𝙤𝙢𝙚𝙣𝙩.")

# Start the bot
def run_bot():
    while True:
        try:
            print("✅ ʙᴏᴛ ɪs ʀᴜɴɴɪɴɢ...")
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"⚠️ ᴇʀʀᴏʀ: {e}")
            time.sleep(5)  

if __name__=="__main__":
    run_bot()