import io
from urllib.parse import quote

import telebot
from telebot import types
from storage import user_region, token, user_data, user_route
from data_fetcher import get_attractions, get_place_image, download_image_bytes

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, 'This bot can help you to plan your holiday in Belarus')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonCreate = types.KeyboardButton(text="create")
    markup.add(buttonCreate)
    bot.send_message(message.chat.id, "Create new trip?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "create")
def almoust_creating(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonMinsk = types.KeyboardButton(text="Minsk")
    buttonGrodno = types.KeyboardButton(text="Grodno")
    buttonBrest = types.KeyboardButton(text="Brest")
    buttonVitebsk = types.KeyboardButton(text="Vitebsk")
    buttonMogilev = types.KeyboardButton(text="Mogilev")
    buttonGomel = types.KeyboardButton(text="Gomel")

    markup.row(buttonGrodno, buttonMinsk, buttonBrest)
    markup.row(buttonVitebsk, buttonMogilev, buttonGomel)

    bot.send_message(message.chat.id, "Choose a region for your route", reply_markup=markup)
    bot.register_next_step_handler(message, save_region)


def save_region(message):
    regions = ["Minsk", "Grodno", "Brest", "Vitebsk", "Mogilev", "Gomel"]
    if message.text not in regions:
        bot.send_message(message.chat.id, "Please, choose a valid region from the keyboard.")
        bot.register_next_step_handler(message, save_region)
        return

    user_region[message.chat.id] = message.text
    user_route[message.chat.id] = []
    bot.send_message(message.chat.id, f"Region {message.text} saved!")

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttonPrevious = types.KeyboardButton(text="<")
    buttonAdd = types.KeyboardButton(text="+")
    buttonNext = types.KeyboardButton(text=">")
    buttonCreateRoute = types.KeyboardButton(text="create route")
    markup.row(buttonPrevious, buttonAdd, buttonNext)
    markup.row(buttonCreateRoute)

    bot.send_message(message.chat.id, "🔍 Loading attractions from Wikipedia... Please wait.", reply_markup=markup)

    try:
        places_list = get_attractions(message.text)
    except Exception as e:
        places_list = None
        bot.send_message(message.chat.id, f"Error in Wikipedia: {e}")

    if places_list:
        user_data[message.chat.id] = {
            "places": places_list,
            "current_index": 0
        }
        show_place(message.chat.id)
    else:
        bot.send_message(
            message.chat.id,
            "No attractions found for this region."
        )


def show_place(chat_id):
    data = user_data.get(chat_id)
    if not data or not data["places"]:
        bot.send_message(chat_id, "No data available. Use 'create' to start over.")
        return

    idx = data["current_index"]
    place = data["places"][idx]
    total = len(data["places"])
    try:
        image_url, description = get_place_image(place["name"])
    except Exception as e:
        print(f"[show_place] get_place_image failed for '{place['name']}': {e}")
        image_url, description = None, "Description temporary unavailable."

    caption = f"📍 *{place['name']}*\n\n📝 {description}\n\n🔢 Place {idx + 1} of {total}"

    if len(caption) > 1024:
        caption = caption[:1000] + "..."

    if image_url:
        image_bytes = download_image_bytes(image_url)
        if image_bytes:
            try:
                bot.send_photo(chat_id, io.BytesIO(image_bytes), caption=caption, parse_mode="Markdown")
                return
            except Exception as e:
                print(f"Error cant send a photo ({image_url}): {e}")

    bot.send_message(chat_id, caption, parse_mode="Markdown")


@bot.message_handler(func=lambda message: message.text in ["<", ">"])
def navigate_places(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id)

    if not data or not data["places"]:
        bot.send_message(chat_id, "Please select a region first using 'create'.")
        return

    current_idx = data["current_index"]
    total_places = len(data["places"])

    if message.text == ">":
        data["current_index"] = (current_idx + 1) % total_places
    elif message.text == "<":
        data["current_index"] = (current_idx - 1 + total_places) % total_places

    show_place(chat_id)


@bot.message_handler(func=lambda message: message.text == "+")
def add_to_route(message):
    chat_id = message.chat.id
    data = user_data.get(chat_id)
    if not data:
        bot.send_message(chat_id, "Choose a region first.")
        return

    idx = data["current_index"]
    current_place = data["places"][idx]["name"]

    route = user_route.setdefault(chat_id, [])
    if current_place in route:
        bot.send_message(chat_id, f" *{current_place}* Already in a route.", parse_mode="Markdown")
    else:
        route.append(current_place)
        bot.send_message(
            chat_id,
            f"Added to your route: *{current_place}*\n total amount of saved places: {len(route)}",
            parse_mode="Markdown"
        )


def build_google_maps_url(places, region):
    segments = [quote(f"{name}, {region}, Belarus") for name in places]
    return "https://www.google.com/maps/dir/" + "/".join(segments)


@bot.message_handler(func=lambda message: message.text == "create route")
def handle_create_route(message):
    chat_id = message.chat.id
    route = user_route.get(chat_id, [])

    if not route:
        bot.send_message(
            chat_id,
            "You haven't added any places to the route yet. "
            " Scroll through the sights using (< / >) and press '+', to save places you like"
        )
        return

    region = user_region.get(chat_id, "")
    maps_url = build_google_maps_url(route, region)

    places_text = "\n".join(f"{i + 1}. {name}" for i, name in enumerate(route))
    bot.send_message(
        chat_id,
        f"Your route is ready!\n\n{places_text}\n\n🗺️ Open in  Google Maps:\n{maps_url}"
    )


if __name__ == '__main__':
    bot.remove_webhook()
    bot.infinity_polling(none_stop=True)