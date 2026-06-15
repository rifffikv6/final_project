import telebot
import time
import os
from logick import teras_model

bot = telebot.TeleBot('')  


MODEL_PATH = "D:\progs\itogovi _proekte\converted_keras\keras_model.h5"          
LABELS_PATH = "converted_keras/labels.txt"       

awaiting_fire_location = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, f"Меня зовут {bot.get_me().first_name}, моя задача — рассказать о влиянии катаклизмов и человека на глобальное потепление.\n\n"
                          f"📌 Команды:\n"
                          f"/info — информация о глобальном потеплении\n\n"
                          f"🔥 А ещё я могу распознать пожар на фото! Просто отправьте мне изображение леса или пожара.")

@bot.message_handler(commands=['info'])
def send_info(message):
    bot.reply_to(message, """🌍 **Глобальное потепление** — это повышение средней температуры Земли, вызванное парниковым эффектом.

**Основные антропогенные факторы:**
• Сжигание ископаемого топлива → CO₂
• Вырубка лесов
• Сельское хозяйство (метан, N₂O)
• Промышленность

**Последствия:** рост температуры, экстремальные погодные явления, таяние ледников.

**Как бороться:**
• Возобновляемая энергетика
• Восстановление лесов
• Переработка отходов
• Электротранспорт
• Экономия ресурсов

🌱 **Лесные пожары** — одна из причин глобального потепления. Присылайте фото леса, и я помогу определить пожар!""", parse_mode='Markdown')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    
    bot.send_chat_action(message.chat.id, 'typing')
    
    bot.reply_to(message, "🔍 Анализирую фотографию... Подождите немного.")

    
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    
    temp_img_path = "temp_photo.jpg"
    with open(temp_img_path, 'wb') as f:
        f.write(downloaded_file)

    try:
        
        class_name, confidence = teras_model(temp_img_path, MODEL_PATH, LABELS_PATH)
        
       
        
        class_name = class_name.strip()  
        
        print(f"Распознано: {class_name}, уверенность: {confidence:.2f}")  

        if class_name == "пожар":
            
            alert_text = (
                f"🔥🔥🔥 **ВНИМАНИЕ! ОБНАРУЖЕН ПОЖАР!** 🔥🔥🔥\n\n"
                f"Уверенность: {confidence:.2%}\n\n"
                f"🚨 **НЕМЕДЛЕННЫЕ ДЕЙСТВИЯ:**\n\n"
                f"1️⃣ **НЕ ПЫТАЙТЕСЬ ПОТУШИТЬ САМИ**, если огонь сильный!\n"
                f"2️⃣ **НЕМЕДЛЕННО ПОКИНЬТЕ ОПАСНУЮ ЗОНУ**\n"
                f"3️⃣ **ДЫШИТЕ ЧЕРЕЗ ВЛАЖНУЮ ТКАНЬ** — дым очень опасен\n"
                f"4️⃣ **ЗВОНИТЕ В ПОЖАРНУЮ ОХРАНУ:**\n"
                f"   📞 **101** (МЧС России)\n"
                f"   📞 **112** (единый номер экстренных служб)\n\n"
                f"5️⃣ **СООБЩИТЕ ДИСПЕТЧЕРУ:**\n"
                f"   • Точный адрес или ориентиры\n"
                f"   • Что горит (лес, трава, здание)\n"
                f"   • Примерный размер пожара\n\n"
                f"⚠️ **НЕ ВОЗВРАЩАЙТЕСЬ В ОПАСНУЮ ЗОНУ!**\n\n"
                f"📍 Пожалуйста, **напишите текстом**, где вы видите пожар (город, район, улица, ориентиры)."
            )
            bot.reply_to(message, alert_text, parse_mode='Markdown')
            
            
            awaiting_fire_location[message.chat.id] = True

        else:  
            bot.reply_to(
                message, 
                f"✅ **На фото нет пожара**\n\n"
                f"Распознано: {class_name}\n"
                f"Уверенность: {confidence:.2%}\n\n"
                f"🌲 Помните: леса — это лёгкие планеты! "
                f"Сохраняя леса от пожаров, мы боремся с глобальным потеплением.\n\n"
                f"Продолжайте следить за природой и сообщать о пожарах!",
                parse_mode='Markdown'
            )

    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при анализе фото: {str(e)}\n\nПопробуйте отправить другое изображение.")
        print(f"Ошибка: {e}")
    finally:
        
        if os.path.exists(temp_img_path):
            os.remove(temp_img_path)


@bot.message_handler(func=lambda message: awaiting_fire_location.get(message.chat.id, False))
def handle_fire_location(message):
    location_text = message.text
    
    response_text = (
        f"🙏 **Спасибо за информацию!**\n\n"
        f"📍 Сообщение о пожаре по адресу:\n"
        f"`{location_text}`\n\n"
        f"🚒 **Информация передана в службу мониторинга.**\n\n"
        f"⚠️ **Ещё раз:** немедленно звоните по номеру **101** или **112**!\n"
        f"Не оставайтесь рядом с пожаром — ваша безопасность превыше всего!\n\n"
        f"🔥 Помните: лесные пожары — одна из причин глобального потепления. "
        f"Своевременное сообщение о пожаре спасает природу и жизни людей!"
    )
    bot.send_message(message.chat.id, response_text, parse_mode='Markdown')
    
    
    del awaiting_fire_location[message.chat.id]


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "❓ Такой команды в моём списке нет.\n\n"
                          "📸 Отправьте мне **фото леса или пожара** — я помогу определить опасность.\n"
                          "ℹ️ Или используйте команду /info для информации о глобальном потеплении.")

if __name__ == "__main__":
    print("🤖 Бот запущен и готов к работе...")
    print(f"Модель: {MODEL_PATH}")
    print(f"Метки: {LABELS_PATH}")
    bot.polling(none_stop=True) 
