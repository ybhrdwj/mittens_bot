import logging
import sqlite3
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from datetime import datetime, time, timedelta
from flask import Flask, jsonify, request, send_file
from config import BOT_TOKEN, WEBAPP_URL, DB_NAME

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def get_last_4am():
    now = datetime.now()
    last_4am = now.replace(hour=4, minute=0, second=0, microsecond=0)
    if now.time() < time(4, 0):
        last_4am -= timedelta(days=1)
    return last_4am

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                (user.id, user.username))
    conn.commit()
    conn.close()
    
    keyboard = [
        [InlineKeyboardButton("Open Mittens App", web_app=WebAppInfo(url=WEBAPP_URL))],
        [InlineKeyboardButton("Set Goals", callback_data="set_goals")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome to Mittens Bot, {user.first_name}! Use the buttons below to manage your goals.",
        reply_markup=reply_markup
    )

async def set_goals(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Please enter your goals in the format: {Frequency} {GoalName}\n"
                                    "For example: 2x Gym\n"
                                    "You can set up to 4 goals. Enter 'done' when finished.")
    context.user_data['setting_goals'] = True
    context.user_data['goals'] = []

async def handle_goal_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'setting_goals' not in context.user_data or not context.user_data['setting_goals']:
        return

    text = update.message.text.strip().lower()
    
    if text == 'done':
        if not context.user_data['goals']:
            await update.message.reply_text("You haven't set any goals yet. Please set at least one goal.")
            return
        
        user_id = update.effective_user.id
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("DELETE FROM goals WHERE user_id = ?", (user_id,))
        
        for goal in context.user_data['goals']:
            cur.execute("INSERT INTO goals (user_id, name, frequency_aimed) VALUES (?, ?, ?)",
                        (user_id, goal['name'], goal['frequency']))
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text("Your goals have been set successfully!")
        context.user_data['setting_goals'] = False
        context.user_data['goals'] = []
    else:
        try:
            frequency, name = text.split(' ', 1)
            frequency = int(frequency[0])
            if frequency <= 0:
                raise ValueError
            
            if len(context.user_data['goals']) >= 4:
                await update.message.reply_text("You've already set 4 goals. Enter 'done' to finish.")
            else:
                context.user_data['goals'].append({'frequency': frequency, 'name': name})
                await update.message.reply_text(f"Goal added: {frequency}x {name}\n"
                                                f"You have set {len(context.user_data['goals'])} goals. "
                                                f"Enter another goal or 'done' to finish.")
        except (ValueError, IndexError):
            await update.message.reply_text("Invalid format. Please use the format: {Frequency} {GoalName}")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    data = json.loads(update.effective_message.web_app_data.data)
    if data['action'] == 'log_goal':
        goal_id = data['goal_id']
        now = datetime.now()
        last_4am = get_last_4am()
        
        if now - last_4am > timedelta(days=1):
            await update.message.reply_text("Sorry, it's past 4 AM. You can't log goals for yesterday anymore.")
            return

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO logs (goal_id, timestamp) VALUES (?, ?)", 
                    (goal_id, now.isoformat()))
        cur.execute("UPDATE goals SET frequency_done = frequency_done + 1 WHERE id = ?", (goal_id,))
        conn.commit()

        cur.execute("SELECT name, frequency_aimed, frequency_done FROM goals WHERE id = ?", (goal_id,))
        goal = cur.fetchone()
        conn.close()

        await update.message.reply_text(f"Progress logged for {goal['name']}!\n"
                                        f"You've completed this goal {goal['frequency_done']}/{goal['frequency_aimed']} times this week.")

@app.route('/get_goals')
def get_goals():
    user_id = request.args.get('user_id')
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, frequency_aimed, frequency_done FROM goals WHERE user_id = ?", (user_id,))
    goals = [dict(row) for row in cur.fetchall()]
    conn.close()
    return jsonify(goals)

@app.route('/')
def serve_webapp():
    return send_file('webapp.html')

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("set", set_goals))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal_input))
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))

    application.run_polling()

if __name__ == '__main__':
    main()