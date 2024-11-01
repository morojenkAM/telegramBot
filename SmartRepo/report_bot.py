from transformers import pipeline
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, CallbackQueryHandler
from docxtpl import DocxTemplate
from typing import Final
import os

TOKEN: Final = ""
BOT_USERNAME: Final = "@IAraport_bot"

raport_data = {
    "studentul": "",
    "continut": "",
    "concluzie": "",
    "denumirea_cursului": "",
    "grupa_studentului": "",
    "numarul_lucrarii": "",
    "profesorul": "",
}


summarizer = pipeline("summarization", model="t5-small")
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ro")

def generate_conclusion(content: str) -> str:
    print("[DEBUG] Generare concluzie pentru conținut:", content)
    summary = summarizer(content, max_length=100, min_length=50, do_sample=False)
    conclusion = summary[0]['summary_text']
    
    conclusion = conclusion[0].upper() + conclusion[1:]
    
    print("[DEBUG] Concluzie generată:", conclusion)
    return conclusion



async def start_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Salut! Folosește comanda /help pentru a vedea ce pot face.")

async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Comenzile disponibile sunt:\n"
        "/continut - Adaugă conținutul principal\n"
        "/concluzie - Adaugă concluzia\n"
        "/genereaza_concluzie - Genereaza o concluzie automat\n"
        "/denumire_curs - Setează denumirea cursului\n"
        "/grupa_student - Setează grupa studentului\n"
        "/numar_lucrare - Setează numărul laboratorului\n"
        "/profesor - Setează numele profesorului\n"
        "/student - Setează numele studentului\n"
        "/intrebari - Intrebarile disponibile\n"
        "/finalizare - Generează și trimite raportul final"
    )

async def set_continut(update: Update, context: CallbackContext):
    continut = " ".join(context.args)
    if continut:
        raport_data['continut'] = continut
        print("[DEBUG] Conținut setat:", continut)
        await update.message.reply_text("Conținutul a fost adăugat.")
    else:
        await update.message.reply_text("Folosește comanda /continut urmată de textul dorit pentru conținut.")

async def ask_generate_conclusion(update: Update):
    keyboard = [
        [InlineKeyboardButton("Da", callback_data='yes')],
        [InlineKeyboardButton("Nu", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Nu există concluzie. Dorești să o generezi automat?", reply_markup=reply_markup)

async def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  

    if query.data == 'yes':
        if not raport_data['continut']:
            await query.message.reply_text("Nu există conținut pentru a genera o concluzie. Te rog să adaugi conținutul folosind comanda /continut.")
            return
        
        await query.message.reply_text("Se generează concluzia...")
        raport_data["concluzie"] = generate_conclusion(raport_data["continut"])
        await query.message.reply_text(f"Concluzia generată este: {raport_data['concluzie']}")
    
    elif query.data == 'no':
        await query.message.reply_text("Concluzia nu a fost generată.")


async def set_concluzie(update: Update, context: CallbackContext):
    concluzie = " ".join(context.args)
    if concluzie:
        raport_data['concluzie'] = concluzie
        print("[DEBUG] Concluzie setată:", concluzie)
        await update.message.reply_text("Concluzia a fost adăugată.")
    else:
        await update.message.reply_text("Folosește comanda /concluzie urmată de textul dorit pentru concluzie.")


async def set_denumire_curs(update: Update, context: CallbackContext):
    denumirea_cursului = " ".join(context.args)
    if denumirea_cursului:
        raport_data['denumirea_cursului'] = denumirea_cursului
        print("[DEBUG] Denumire curs setată:", denumirea_cursului)
        await update.message.reply_text(f"Denumirea cursului a fost setată: {denumirea_cursului}")
    else:
        await update.message.reply_text("Folosește comanda /denumire_curs urmată de textul dorit pentru denumirea cursului.")

async def set_grupa_student(update: Update, context: CallbackContext):
    grupa_studentului = " ".join(context.args)
    if grupa_studentului:
        raport_data['grupa_studentului'] = grupa_studentului
        print("[DEBUG] Grupa student setată:", grupa_studentului)
        await update.message.reply_text(f"Grupa studentului a fost setată: {grupa_studentului}")
    else:
        await update.message.reply_text("Folosește comanda /grupa_student urmată de textul dorit pentru grupa studentului.")

async def set_numar_lucrare(update: Update, context: CallbackContext):
    numarul_lucrarii = " ".join(context.args)
    if numarul_lucrarii:
        raport_data['numarul_lucrarii'] = numarul_lucrarii
        print("[DEBUG] Număr lucrare setat:", numarul_lucrarii)
        await update.message.reply_text(f"Numărul lucrării a fost setat: {numarul_lucrarii}")
    else:
        await update.message.reply_text("Folosește comanda /numar_lucrare urmată de textul dorit pentru numărul lucrării.")

async def set_profesor(update: Update, context: CallbackContext):
    profesorul = " ".join(context.args)
    if profesorul:
        raport_data['profesorul'] = profesorul
        print("[DEBUG] Profesor setat:", profesorul)
        await update.message.reply_text(f"Profesorul a fost setat: {profesorul}")
    else:
        await update.message.reply_text("Folosește comanda /profesor urmată de numele profesorului.")

async def set_student(update: Update, context: CallbackContext):
    studentul = " ".join(context.args)
    if studentul:
        raport_data['studentul'] = studentul
        print("[DEBUG] Student setat:", studentul)
        await update.message.reply_text(f"Studentul a fost setat: {studentul}")
    else:
        await update.message.reply_text("Folosește comanda /student urmată de numele studentului.")

def completare_template(data):
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    template_path = "template_raport.docx"
    file_path = os.path.join(desktop_path, "raport_final.docx")

    print("[DEBUG] Încercare deschidere fișier template:", template_path)

    try:
        doc = DocxTemplate(template_path)
        doc.render(data)  
        doc.save(file_path)
        print("[DEBUG] Fișierul final generat la:", file_path)
        return file_path
    except Exception as e:
        print(f"[EROARE] Nu s-a putut deschide sau salva fișierul: {e}")
        raise e

async def genereaza_concluzie_command(update: Update, context: CallbackContext):
    if not raport_data['continut']:
        await update.message.reply_text("Nu există conținut pentru a genera o concluzie. Te rog să adaugi conținutul folosind comanda /continut.")
        return

    keyboard = [
        [InlineKeyboardButton("Da", callback_data='yes')],
        [InlineKeyboardButton("Nu", callback_data='no')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Dorești să generezi concluzia automat?", reply_markup=reply_markup)

async def finalizare(update: Update, context: CallbackContext):
    if not raport_data["concluzie"]:
        await ask_generate_conclusion(update)
        return

    incomplete_fields = [field for field, value in raport_data.items() if not value]
    
    if incomplete_fields:
        fields_text = ", ".join(incomplete_fields)
        if update.message:
            await update.message.reply_text(f"Te rog să completezi toate secțiunile necesare. Lipsesc următoarele: {fields_text}.")
        elif update.callback_query:
            await update.callback_query.message.reply_text(f"Te rog să completezi toate secțiunile necesare. Lipsesc următoarele: {fields_text}.")
        print("[DEBUG] Date lipsă în raport_data:", raport_data)
        return

    try:
        file_path = completare_template(raport_data)
        if update.message:
            await update.message.reply_text("Raportul este gata! Îți trimit acum documentul.")
            await context.bot.send_document(chat_id=update.message.chat_id, document=open(file_path, "rb"))
        elif update.callback_query:
            await update.callback_query.message.reply_text("Raportul este gata! Îți trimit acum documentul.")
            await context.bot.send_document(chat_id=update.callback_query.message.chat_id, document=open(file_path, "rb"))
    except FileNotFoundError as e:
        print("[EROARE] Fișierul template_raport.docx nu a fost găsit.")
        if update.message:
            await update.message.reply_text("Nu am putut găsi fișierul template. Asigură-te că este plasat corect pe desktop.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("Nu am putut găsi fișierul template. Asigură-te că este plasat corect pe desktop.")
    except Exception as e:
        print(f"[EROARE] Eroare la generarea documentului: {e}")
        if update.message:
            await update.message.reply_text("A apărut o eroare în generarea raportului.")
        elif update.callback_query:
            await update.callback_query.message.reply_text("A apărut o eroare în generarea raportului.")


def handle_respons(text: str) -> str:
    processed = text.lower()
    if 'salut' in processed:
        return 'Salut! Cum te pot ajuta cu raportul?'
    elif 'mulțumesc' in processed:
        return 'Cu plăcere !!!'
    elif 'cum te numești?' in processed: 
        return 'Mă numesc SmartReport'
    elif 'cine te-a creat?' in processed:
        return 'M-a creat echipa Erorr 404'
    elif 'ce poți face?' in processed:
        return 'Pot genera rapoarte. Folosește /help pentru a vedea comenzile.'
    elif 'nu am concluzie' in processed:
        return 'Folosește comanda /genereaza_concluzie pentru a genera o concluzie, asigură-te că raportul are un continut.'
    elif 'cum creez un raport?' in processed:
        return 'Pentru a crea un raport, folosește comanda /student pentru numele studentului, /continut pentru conținut și /finalizare pentru a genera documentul final. Pentru mai multe detalii folosește comanda /help'
    elif 'pot adauga o concluzie automata' in processed:
        return 'Dacă nu adaugi o concluzie manuală, voi genera una automată din conținutul raportului.'
    elif 'unde se salveaza raportul' in processed:
        return 'Raportul se va salva pe desktop-ul tău, în fișierul raport_final.docx.'
    elif 'cum pot vedea toate comenzile' in processed:
        return 'Pentru o listă completă de comenzi, folosește comanda /help.'
    elif 'cat timp dureaza generarea unui raport' in processed:
        return 'Generarea raportului durează doar câteva momente, iar la final vei primi un mesaj cu documentul.'
    elif 'pot modifica raportul dupa ce a fost generat' in processed:
        return 'După ce raportul a fost generat, poți modifica documentul manual. Dacă ai nevoie de modificări suplimentare, va trebui să le faci prin comenzile corespunzătoare.'
    elif 'cum pot adauga imagini' in processed:
        return 'Momentan, botul nu suportă adăugarea de imagini direct în raport. Poți adăuga doar text.'
    elif 'este botul disponibil 24/7' in processed:
        return 'Da, botul este disponibil oricând! Îți voi răspunde în orice moment.'
    elif 'pot salva mai multe rapoarte' in processed:
        return 'Da, poți genera și salva mai multe rapoarte. Fiecare raport va fi salvat cu numele raport_final.docx, dar îți recomand să schimbi numele fișierului manual pentru a le distinge.'
    elif 'pot anula o comanda' in processed:
        return 'Dacă ai început un raport și dorești să anulezi, pur și simplu nu continua cu comenzile. Botul nu va genera nimic până când nu folosești comanda /finalizare.'
    elif 'care sunt formatele acceptate' in processed:
        return 'Raportul va fi salvat în format .docx, care este compatibil cu majoritatea editorilor de documente.'
    elif 'cum pot modifica datele introduse' in processed:
        return 'Poți modifica datele introduse folosind comenzile corespunzătoare pentru fiecare secțiune, cum ar fi /titlu, /autor, /continut etc.'
    
    return 'Nu înțeleg întrebarea. Folosește /help pentru comenzi.'


async def intrebari_command(update: Update, context: CallbackContext):
    intrebari_text = (
        "Poți adresa următoarele întrebări:\n"
        "- Salut\n"
        "- Mulțumesc\n"
        "- Cum te numești?\n"
        "- Cine te-a creat?\n"
        "- Ce poți face?\n"
        "- Nu am concluzie\n"
        "- Cum creez un raport?\n"
        "- Pot adăuga o concluzie automată?\n"
        "- Unde se salvează raportul?\n"
        "- Cum pot vedea toate comenzile?\n"
        "- Cât timp durează generarea unui raport?\n"
        "- Pot modifica raportul după ce a fost generat?\n"
        "- Cum pot adăuga imagini?\n"
        "- Este botul disponibil 24/7?\n"
        "- Pot salva mai multe rapoarte?\n"
        "- Pot anula o comandă?\n"
        "- Care sunt formatele acceptate?\n"
        "- Cum pot modifica datele introduse?\n"
    )
    await update.message.reply_text(intrebari_text)



if __name__ == '__main__':
    print("[DEBUG] Pornire bot")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("continut", set_continut))
    app.add_handler(CommandHandler("concluzie", set_concluzie))
    app.add_handler(CommandHandler("genereaza_concluzie", genereaza_concluzie_command))
    app.add_handler(CommandHandler("denumire_curs", set_denumire_curs))
    app.add_handler(CommandHandler("grupa_student", set_grupa_student))
    app.add_handler(CommandHandler("numar_lucrare", set_numar_lucrare))
    app.add_handler(CommandHandler("profesor", set_profesor))
    app.add_handler(CommandHandler("student", set_student))
    app.add_handler(CommandHandler("finalizare", finalizare))
    
    app.add_handler(CommandHandler("intrebari", intrebari_command))


    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, 
                                   lambda update, context: 
                                   update.message.reply_text(handle_respons(update.message.text))))

    app.add_handler(CallbackQueryHandler(button_handler))


    print("Start polling")
    app.run_polling(poll_interval = 3)
