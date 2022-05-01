#Kanged From @TroJanZheX
import asyncio
import re
import ast

from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, CUSTOM_FILE_CAPTION, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, SINGLE_BUTTON
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, temp
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import(
   del_all,
   find_filter,
   get_filters,
)

import datetime
now = datetime.datetime.now()
hour = now.hour

if hour < 12:
    greeting = "Good morning"
elif hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good night"

FILE_CHANNEL_ID = int(-1001731956857)

BUTTONS = {}


@Client.on_message(filters.command('hin'))
async def hin(client, message):
    msg = await message.reply_text("""
मुझे आपके द्वारा अनुरोधित फ़ाइल नहीं मिली 😕
निम्नलिखित करने का प्रयास करें...

=> सही वर्तनी के साथ अनुरोध

=> उन फिल्मों के बारे में न पूछें जो ओटीटी प्लेटफॉर्म पर रिलीज नहीं हुई हैं

=> इस प्रारूप में [मूवीनाम, भाषा] में पूछने का प्रयास करें।

=> Google पर खोजने के लिए नीचे दिए गए बटन का प्रयोग करें 😌
""", parse_mode="md",
     reply_markup = InlineKeyboardMarkup(
      [[
        InlineKeyboardButton('🔍 Search On Google', url="https://google.com/search?q={search}")
      ],
      [
        InlineKeyboardButton('✘ Close ✘', callback_data='close_data')
     ]]))

    await asyncio.sleep(50)
    await msg.delete()



@Client.on_message(filters.command('english'))
async def english(client, message):
    msg = await message.reply_text("""
I couldn't find the file you requested 😕
Try to do the following...

=> Request with correct spelling

=> Don't ask movies that are not released in OTT platforms

=> Try to ask in [MovieName, Language] this format.

=> Use the button below to search on Google 😌
""", parse_mode="md",
     reply_markup = InlineKeyboardMarkup(
      [[
        InlineKeyboardButton('🔍 Search On Google', url="https://google.com/search?q={search}")
      ],
      [
        InlineKeyboardButton('✘ Close ✘', callback_data='close_data')
     ]]))

    await asyncio.sleep(50)
    await msg.delete()


@Client.on_message(filters.command('mal'))
async def mal(client, message):
    msg = await message.reply_text("""
താങ്കൾ ആവശ്യപ്പെട്ട ഫയൽ എനിക്ക് കണ്ടെത്താനായില്ല 😕
താഴെ പറയുന്ന കാര്യങ്ങളിൽ ശ്രദ്ധിക്കുക...

=> കറക്റ്റ് സ്പെല്ലിംഗിൽ ചോദിക്കുക.

=> ഒ.ടി.ടി പ്ലാറ്റ്ഫോമുകളിൽ റിലീസ് ആകാത്ത സിനിമകൾ ചോദിക്കരുത്.

=> കഴിവതും [സിനിമയുടെ പേര്, ഭാഷ] ഈ രീതിയിൽ ചോദിക്കുക.

=> ഗൂഗിളിൽ സെർച്ച് ചെയ്യാനായി താഴെ കാണുന്ന ബട്ടൺ ഉപയോഗിക്കാം 😌
""", parse_mode="md",
     reply_markup = InlineKeyboardMarkup(
      [[
        InlineKeyboardButton('🔍 Search On Google', url="https://google.com/search?q={search}")
      ],
      [
        InlineKeyboardButton('✘ Close ✘', callback_data='close_data')
     ]]))

    await asyncio.sleep(50)
    await msg.delete()


@Client.on_message(filters.command('tam'))
async def tam(client, message):
    msg = await message.reply_text("""
நீங்கள் கோரிய கோப்பை என்னால் கண்டுபிடிக்க முடியவில்லை 😕
பின்வருவனவற்றை செய்ய முயற்சிக்கவும்...

=> சரியான எழுத்துப்பிழையுடன் கோரிக்கை

=> OTT இயங்குதளங்களில் வெளியிடப்படாத திரைப்படங்களைக் கேட்க வேண்டாம்

=> [MovieName, Language] இந்த வடிவமைப்பில் கேட்க முயற்சிக்கவும்.

=> Google இல் தேட கீழே உள்ள பொத்தானைப் பயன்படுத்தவும் 😌
""", parse_mode="md",
     reply_markup = InlineKeyboardMarkup(
      [[
        InlineKeyboardButton('🔍 Search On Google', url="https://google.com/search?q={search}")
      ],
      [
        InlineKeyboardButton('✘ Close ✘', callback_data='close_data')
     ]]))

    await asyncio.sleep(50)
    await msg.delete()


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client,message):
    group_id = message.chat.id
    name = message.text

    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await message.reply_text(reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await message.reply_text(
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button)
                            )
                    elif btn == "[]":
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or ""
                        )
                    else:
                        button = eval(btn) 
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button)
                        )
                except Exception as e:
                    print(e)
                break 

    else:
        await auto_filter(client, message)   

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):

    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("oKda", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using this for one of my old message, please send the request again.",show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    if SINGLE_BUTTON:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}")]
        )
        btn.append(
            [InlineKeyboardButton(f"🔰 Pages {round(int(offset)/10)+1} / {round(total/10)}🔰", callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(text="NEXT ⏩",callback_data=f"next_{req}_{key}_{offset}")]
        )
        btn.append(
            [InlineKeyboardButton(text=f"🔰 Pages 1/{round(int(total_results)/10)}🔰",callback_data="pages")]
        )
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ], 
        )
        btn.append(
            [InlineKeyboardButton(f"🔰 Pages {round(int(offset)/10)+1} / {round(total/10)}🔰", callback_data="pages")]
        )
    btn.insert(0, 
            [
                InlineKeyboardButton(text=f"📂 File: {len(files)}", callback_data="fil"),
                InlineKeyboardButton("🔆 Tips", callback_data="tip")
            ])

    btn.insert(0, [
        InlineKeyboardButton(text=f"🔮 {search} 🔮", callback_data="so")
    ])
    try:
        await query.edit_message_reply_markup( 
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            grpid  = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups",
                    quote=True
                )
                return

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == "creator") or (str(userid) in ADMINS):    
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!",show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == "private":
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in ["group", "supergroup"]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == "creator") or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("Thats not for you!!",show_alert=True)


    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        title = query.data.split(":")[2]
        act = query.data.split(":")[3]
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}:{title}"),
                InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode="md"
        )
        return

    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]
        title = query.data.split(":")[2]
        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occured!!', parse_mode="md")
        return
    elif "disconnect" in query.data:
        await query.answer()

        title = query.data.split(":")[2]
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode="md"
            )
        else:
            await query.message.edit_text('Some error occured!!', parse_mode="md")
        return
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text('Some error occured!!', parse_mode="md")
        return
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{title}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert,show_alert=True)

    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        mention = query.from_user.mention
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                buttons = [[
                  InlineKeyboardButton('➕ADD ME TO YOUR GROUP➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                  ]]  
            except Exception as e:
                print(e)
            f_caption=f_caption
            size = size
            mention = mention
        if f_caption is None:
            f_caption = f"{files.file_name}"
            size = f"{files.file_size}"
            mention = f"{query.from_user.mention}"
            
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            elif P_TTI_SHOW_OFF:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
                return
            else:
                send_file = await client.send_cached_media(
                    chat_id=FILE_CHANNEL_ID,
                    file_id=file_id,
                    caption=f'<b>{title}</b>\n\n<code>{size}</code>\n\n<code>=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=</code>\n\n<b>{greeting} {query.from_user.mention}✨</b>\n\n<i>Because of copyright this file will be deleted from here within 5 minutesSo forward it to anywhere before downloading!</i>\n\n<i>കോപ്പിറൈറ്റ് ഉള്ളതുകൊണ്ട് ഈ ഫയൽ 5 മിനിറ്റിനുള്ളിൽ ഇവിടെനിന്നും ഡിലീറ്റ് ആകുന്നതാണ്അതുകൊണ്ട് ഇവിടെ നിന്നും മറ്റെവിടെക്കെങ്കിലും മാറ്റിയതിന് ശേഷം ഡൗൺലോഡ് ചെയ്യുക!</i>\n\n<b><b>🔰 Powered By:</b>{query.message.chat.title}</b>',
                    reply_markup = InlineKeyboardMarkup(buttons)   
                    )
                btn = [[
                    InlineKeyboardButton("🔥 GET FILE 🔥", url=f'{send_file.link}')
                    ],[
                    InlineKeyboardButton("✘ Close ✘", callback_data='close_data')
                ]]
                reply_markup = InlineKeyboardMarkup(btn)
                bb = await query.message.reply_text(
                    text=script.ANYFILECAPTION_TXT.format(file_name=title, file_size=size, file_caption=f_caption),
                reply_markup = reply_markup
                )
                await asyncio.sleep(300)
                await send_file.delete()
                await bb.delete()

        except UserIsBlocked:
            await query.answer('Unblock the bot mahn !',show_alert = True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("I Like Your Smartness, But Don't Be Oversmart 😒",show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name=title, file_size=size, file_caption=f_caption)
                buttons = [[
                  InlineKeyboardButton('➕ADD ME TO YOUR GROUP➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                  ]]
            except Exception as e:
                print(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption
            )

    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕ 𝖠𝖽𝖽 𝗆𝖾 𝗍𝗈 𝗒𝗈𝗎𝗋 𝖦𝗋𝗈𝗎𝗉 ➕', url='http://t.me/Angelina_v2_bot?startgroup=true')
            ],[
            InlineKeyboardButton('ʜᴇʟᴘ 💭', callback_data='help'),
            InlineKeyboardButton("🧣ᴀʙᴏᴜᴛ", callback_data="about")
            ],[
            InlineKeyboardButton('🔍sᴇᴀʀᴄʜ', switch_inline_query_current_chat='')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await massage.reply_chat_action("typing")
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
            InlineKeyboardButton('Auto Filter', callback_data='autofilter')
            ],[
            InlineKeyboardButton('Connection', callback_data='coct'),
            InlineKeyboardButton('Extra Mods', callback_data='extra')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔮 Status', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "about":
        buttons= [[
            InlineKeyboardButton('🤖 Updates', url='https://t.me/peterparker088github'),
            InlineKeyboardButton('♥️ Source', callback_data='source')
            ],[
            InlineKeyboardButton('🏠 Home', callback_data='start'),
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('⏹️ Buttons', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('👮‍♂️ Admin', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "fil":
        await query.answer("This movie have total : {total_results} ", show_alert=True
        )
    elif query.data == "ins":
        await query.answer("👇 Select your language below 👇", show_alert=True
        )
    elif query.data == "tip":
        await query.answer("""=> Ask with Correct Spelling
=> Don't ask movie's those are not released in OTT 🤧
=> For better results :
      - Movie name language
      - Eg: Solo Malayalam""", show_alert=True
        )
    elif query.data == "so":
        await query.answer(f"""🏷 Title: {query} 
🎭 Genres: {genres} 
📆 Year: {year} 
🌟 Rating: {rating} 
☀️ Languages : {languages} 
📀 RunTime: {runtime} Minutes
📆 Release Info : {release_date} 
""",show_alert=True
       )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode='html'
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('👩‍🦯 Back', callback_data='help'),
            InlineKeyboardButton('♻️', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        m=await query.message.reply_text("▣▢▢")
        n=await m.edit("▣▣▢")
        o=await n.edit("▣▣▣")
        await asyncio.sleep(1)
        await o.delete()
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode='html'
      )
    

async def auto_filter(client, message):
    if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
        return
    if 2 < len(message.text) < 100:
        
        search = message.text
        files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
        if not files:
            return
        if SINGLE_BUTTON:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            m = await message.reply(
              text=f"""
<b>{greeting} {message.from_user.mention}✨
I couldn't find anything related to your request. 🤧
Try reading the instructions below 👇</b>""",
          reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("📑 Instructions 📑", callback_data='ins')
                    ],
                    [       
                        InlineKeyboardButton("Mal", callback_data="mal"),
                        InlineKeyboardButton("Tam", callback_data="tam"),
                        InlineKeyboardButton("Hin", callback_data="hin"),
                        InlineKeyboardButton("Eng", callback_data="english") 
                    ]
                ]
            )
         )          
            await asyncio.sleep(20)
            await m.delete()
        if not btn:
            return


        if offset != "":
            key = f"{message.chat.id}-{message.message_id}"
            BUTTONS[key] = search
            req = message.from_user.id if message.from_user else 0
            btn.append(
                [InlineKeyboardButton(text="NEXT ⏩",callback_data=f"next_{req}_{key}_{offset}")]
            )
            btn.append(
                [InlineKeyboardButton(text=f"🔰 Pages 1/{round(int(total_results)/10)}🔰",callback_data="pages")]
            )
        else:
            btn.append(
                [InlineKeyboardButton(text="🔰 Pages 1/1🔰",callback_data="pages")]
            )
        btn.insert(0, [
            InlineKeyboardButton(text=f"📂 File: {len(files)}", callback_data="fil"),
            InlineKeyboardButton("🔆 Tips", callback_data="tip")
        ])
        btn.insert(0, [
            InlineKeyboardButton(text=f"🔮 {search} 🔮", callback_data="so")
        ])
        imdb = await get_poster(search) if IMDB else None
        if imdb and imdb.get('poster'):
            try:
                await message.reply_photo(photo=imdb.get('poster'), caption=f"""<b>{imdb.get('title')}</b>


<b>🧬 Genre:</b> {imdb.get('genres')}
<b>🌟 Rating:</b> {imdb.get('rating')}
<b>⏱️ Duration:</b> {imdb.get('runtime')}
<b>📆 Release:</b> {imdb.get('year')}
<b>🎙 Language:</b> {imdb.get('languages')}

<b>💭 Requested By:</b> <tg-spoiler>||{message.from_user.mention}||</tg-spoiler>

<b>🔰 Powered By:</b> <b>{message.chat.title}</b>""", reply_markup=InlineKeyboardMarkup(btn))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                pic = imdb.get('poster')
                poster = pic.replace('.jpg', "._V1_UX360.jpg")
                await message.reply_photo(photo=poster, caption=f"""<b>{imdb.get('title')}</b>


<b>🧬 Genre:</b> {imdb.get('genres')}
<b>🌟 Rating:</b> {imdb.get('rating')}
<b>⏱️ Duration:</b> {imdb.get('runtime')}
<b>📆 Release:</b> {imdb.get('year')}
<b>🎙 Language:</b> {imdb.get('languages')}

<b>💭 Requested By:</b> <tg-spoiler>||{message.from_user.mention}||</tg-spoiler>

<b>🔰 Powered By:</b> <b>{message.chat.title}</b>""", reply_markup=InlineKeyboardMarkup(btn))
            except Exception as e:
                print(e)
                await message.reply_sticker(sticker="CAACAgUAAxkBAAIGzGJi4LmteW8DPnYEHWLqC6AB7RhuAAKnAAPIlGQUYKZ2tWflHJ0eBA", reply_markup=InlineKeyboardMarkup(btn))
        elif imdb:
            await message.reply_sticker(sticker="CAACAgUAAxkBAAIGzGJi4LmteW8DPnYEHWLqC6AB7RhuAAKnAAPIlGQUYKZ2tWflHJ0eBA", reply_markup=InlineKeyboardMarkup(btn))
        else:
            await message.reply_sticker(sticker="CAACAgUAAxkBAAIGzGJi4LmteW8DPnYEHWLqC6AB7RhuAAKnAAPIlGQUYKZ2tWflHJ0eBA", reply_markup=InlineKeyboardMarkup(btn))
