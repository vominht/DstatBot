import matplotlib.pyplot as plt
import requests
import asyncio
import json
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

def load_session_data():
    try:
        with open("session.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_session_data(data):
    with open("session.json", "w") as file:
        json.dump(data, file)

async def plot_difference_chart(user_id, differences):
    plt.figure(figsize=(16, 6))
    plt.fill_between(range(len(differences)), differences, color="red", alpha=0.5)  
    plt.plot(differences, color="red", alpha=0.6)  

    avg_difference = sum(differences) / len(differences) if differences else 0
    peak_difference = max(differences, default=0)
    overall_difference = sum(differences)

    plt.text(0.01, 0.95, f'Average Requests: {int(avg_difference)}', transform=plt.gca().transAxes, fontsize=12, fontweight='bold', color="white")
    plt.text(0.01, 0.90, f'Peak Requests: {peak_difference}', transform=plt.gca().transAxes, fontsize=12, fontweight='bold', color="white")
    plt.text(0.01, 0.85, f'Overall Requests: {overall_difference}', transform=plt.gca().transAxes, fontsize=12, fontweight='bold', color="white")

    plt.title("GRAPH CON CAC GI CX DC", color="white")
    plt.xlabel("Thời gian (s)", color="white")
    plt.ylabel("Số requests", color="white")
    plt.grid(True, color="gray")
    plt.xticks(color="white")
    plt.yticks(color="white")
    plt.gca().patch.set_facecolor('black')  
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().spines['top'].set_color('black')
    plt.gca().spines['right'].set_color('black')

    filename = f"chart_{user_id}.png"
    plt.savefig(filename, facecolor='black')
    plt.close()
    return filename

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    session_data = load_session_data()

    if str(user_id) not in session_data:
        session_data[str(user_id)] = {"last_count": 0, "differences": [], "start_time": asyncio.get_running_loop().time()}
        await update.message.reply_text('ATTACK DI KID')

    while True:
        current_time = asyncio.get_running_loop().time()
        if current_time - session_data[str(user_id)]["start_time"] > 60:
            max_difference = max(session_data[str(user_id)]["differences"], default=0)
            total_difference = sum(session_data[str(user_id)]["differences"])
            await update.message.reply_text(f'ket thuc roi kid oi. MAX RPS: {max_difference}. TOTAL REQUESTS: {total_difference}.')

            filename = await plot_difference_chart(user_id, session_data[str(user_id)]["differences"])
            with open(filename, "rb") as file:
                await context.bot.send_photo(chat_id=update.effective_chat.id, photo=file)

            del session_data[str(user_id)]
            save_session_data(session_data)
            break

        try:
            response = requests.get('https://attack.migranten.network/nginx_status')
            if response.status_code == 200:
                data_parts = response.text.split()
                current_count = int(data_parts[9])
                if session_data[str(user_id)]["last_count"] != 0:  
                    difference = current_count - session_data[str(user_id)]["last_count"]
                    session_data[str(user_id)]["differences"].append(difference)
                session_data[str(user_id)]["last_count"] = current_count
                save_session_data(session_data)
            else:
                await update.message.reply_text('Có lỗi khi lấy dữ liệu.')
        except Exception as e:
            await update.message.reply_text(f'Không thể lấy dữ liệu: {e}')

        await asyncio.sleep(1)  

app = ApplicationBuilder().token("7078229366:AAHfuqica0R54OKtHpw6oIdTZnhhiJvqyOs").build()

app.add_handler(CommandHandler("count", count))

print("Bot is running")
app.run_polling()