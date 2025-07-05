import asyncio
import os
from dotenv import load_dotenv
import edge_tts
import telebot
from telebot import types
import logging

load_dotenv()
user_voices = {}
DEFAULT_VOICE = "es-CL-CatalinaNeural"

async def amain(mensaje,chat_id) -> None:
    TEXT = mensaje   
    # Obtener la voz del usuario o usar la predeterminada
    VOICE = user_voices.get(chat_id, DEFAULT_VOICE)
    OUTPUT_FILE = "Audio.mp3"
    """Main function"""
    communicate = edge_tts.Communicate(TEXT, VOICE)
    await communicate.save(OUTPUT_FILE)


TOKEN = os.getenv("TOKEN")


bot = telebot.TeleBot(TOKEN)


bot.set_chat_menu_button(bot.get_me().id, types.MenuButtonCommands(type='commands'))

# Funciones para manejar diferentes comandos que usara el usuario


def send_audio(message, audio_file):
    with open(audio_file, 'rb') as audio:
        bot.send_audio(message.chat.id, audio)

# Manejador de mensajes
@bot.message_handler(commands=['audio'])
def handle_audio(message):
    audio_file = 'Audio.mp3'  
    send_audio(message, audio_file)


@bot.message_handler(commands=["help"])
def send_help(message):
    bot.reply_to(message, "Este es un bot de Telegram que convierte texto a audio. Puedes usar los siguientes comandos:\n\n" \
           "/audio - Envía un mensaje de texto y recibirás un archivo de audio con la conversión.\n" \
           "/help - Muestra este mensaje de ayuda.\n" \
           "/commands - Muestra las opciones disponibles.\n\n" \
           "Para convertir texto a audio, simplemente escribe el texto que deseas convertir y el bot te enviará un archivo de audio con la conversión.\n\n" )

@bot.message_handler(commands=['start'])
def send_welcome(message):

    bot.reply_to(message, "Hola, soy un bot de Telegram! que puede convertir lo que me escribas a audio!! espero ser util!!! escribe /help para ver lo que puedo hacer y usa /commands para ver mis funciones (Este mensaje puede ser mejorado para una mejor experiencia del usuario)")

@bot.message_handler(commands=['commands'])
def send_commands(message):

    markup = types.InlineKeyboardMarkup()

    # Crea botones con opciones
    itembtn1 = types.InlineKeyboardButton('Voces', callback_data='Voces')
    itembtn2 = types.InlineKeyboardButton('Ayuda', callback_data='help')

    # Agrega botones al diseño del teclado
    markup.add(itembtn1, itembtn2)

    bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=markup)


# se usara para escoger las voces
def voices(call):
    # Crea un nuevo teclado en línea para las opciones de voces
    voice_markup = types.InlineKeyboardMarkup()

    # Agrega botones con las opciones de voces (reemplaza con tus voces reales)
    voice_btn1 = types.InlineKeyboardButton('Andrea(ES)', callback_data='voice_es-EC-AndreaNeural')
    voice_btn2 = types.InlineKeyboardButton('Sebastian(ES)', callback_data='voice_es-VE-SebastianNeural')
    voice_btn3 = types.InlineKeyboardButton('Teresa(ES)', callback_data='voice_es-GQ-TeresaNeural')
    voice_btn4 = types.InlineKeyboardButton('Catalina (ES, Por defecto)', callback_data='voice_es-CL-CatalinaNeural')
    voice_btn5 = types.InlineKeyboardButton('Libby(EN)', callback_data='voice_en-AU-NatashaNeural')
    voice_btn6 = types.InlineKeyboardButton('Nanami(JA)', callback_data='voice_ja-JP-NanamiNeural')


    retunr_btn = types.InlineKeyboardButton('Volver', callback_data='return_to_main')

    voice_markup.add(voice_btn1, voice_btn2, voice_btn3, voice_btn4, voice_btn5, voice_btn6,retunr_btn)

    # Envía el mensaje con el nuevo teclado
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Selecciona una voz:",
        reply_markup=voice_markup
    )

def help_message():
    return "Este es un bot de Telegram que convierte texto a audio. Puedes usar los siguientes comandos:\n\n" \
           "/audio - Envía un mensaje de texto y recibirás un archivo de audio con la conversión.\n" \
           "/help - Muestra este mensaje de ayuda.\n" \
           "/commands - Muestra las opciones disponibles.\n\n" \
           "Para convertir texto a audio, simplemente escribe el texto que deseas convertir y el bot te enviará un archivo de audio con la conversión.\n\n" 



#recibe el texto que el usuario escriba y lo convierte a audio
# y lo envia al usuario como un archivo de audio
@bot.message_handler(func=lambda m: True)
def audio(message):
    try:
        bot.reply_to(message, "Haciendo audio")
        texto = message.text

        # Límite de párrafos (separados por doble salto de línea)
        max_parrafos = 12
        parrafos = texto.split('\n\n')  # Separa por dobles saltos de línea
        if len(parrafos) > max_parrafos:
            texto = '\n\n'.join(parrafos[:max_parrafos])
            bot.reply_to(message, f"⚠️ Se procesarán solo los primeros {max_parrafos} párrafos")

        
        max_caracteres = 4000  # Limite de cararteres (para gTTS (5000 es su límite)
        if len(texto) > max_caracteres:
            texto = texto[:max_caracteres]
            bot.reply_to(message, f"⚠️ Texto truncado a {max_caracteres} caracteres")

        asyncio.run(amain(texto, message.chat.id))  # Llama a la función asíncrona para convertir el texto a audio
        audio_file = 'Audio.mp3'
        send_audio(message, audio_file)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Lo Siento! Ocurrió un error: {e}")
        logging.error(f"Error en audio: {e}")

# Función para manejar consultas de devolución de llamada de botones de teclado en línea
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'Voces':
        # Llama a función personalizada para manejar la selección de voces
        voices(call)
    elif call.data.startswith('voice_'):
        selected_voice = call.data.replace('voice_', '') # Quitamos el prefijo 'voice_'
        
        # AQUI ES DONDE SE GUARDA LA VOZ EN user_voices
        user_voices[call.message.chat.id] = selected_voice 
        bot.send_message(call.message.chat.id, f"Voz seleccionada: {selected_voice}. Ahora puedes enviar un texto para convertirlo a audio.")
    elif call.data == 'help':
        # Llama a función personalizada para mostrar el mensaje de ayuda
        bot.send_message(call.message.chat.id, help_message())
    elif call.data == 'return_to_main':
         send_commands(call.message)

# para asegurarse de que este conectado
if __name__ == '__main__':
    print('conetando')
    bot.polling()