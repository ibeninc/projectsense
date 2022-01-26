import logging

from telegram import Update, ChatAction, ParseMode, ForceReply
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackContext,
    Filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update: Update, _: CallbackContext) -> None:
    # update.message.reply_text('Hi! Use /set <seconds> to set a timer')
    update.message.reply_text(
        "Hello "
        + update.message.from_user.first_name
        + " Use /set <seconds> to set a timer"
    )


def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    context.bot.send_message(job.context, text="☕ Pinggggg! Take a break")


def manage_text(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        "Sorry I didn't understand your command. Press /help to learn more"
    )


def manage_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("Invalid Command. Press /help to learn more")


def remove_job_if_exists(name: str, context: CallbackContext) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def set_timer(update: Update, context: CallbackContext) -> None:
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text("Sorry we can not go back to future!")
            return

        job_removed = remove_job_if_exists(str(chat_id), context)
        context.job_queue.run_once(alarm, due, context=chat_id, name=str(chat_id))

        text = "⏰ Timer Alert Activated!"
        if job_removed:
            text += " Old Timer was removed."
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text("Usage: /set <seconds>")


def unset(update: Update, context: CallbackContext) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    text = "⏰ Timer ALert cancelled!" if job_removed else "You have no active timer."
    update.message.reply_text(text)


def help(update: Update, _: CallbackContext) -> None:
    update.message.reply_text(
        "🤷 /about: About developer\n"
        "/set <seconds>: to set reminder\n"
        "/unset: to unset reminder\n"
    )


def about(update: Update, _: CallbackContext) -> None:
    update.message.reply_text("👨‍💻 Developed by \n@rubeecoder")


def main() -> None:
    """Run bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))
    dispatcher.add_handler(CommandHandler("set", set_timer))
    dispatcher.add_handler(CommandHandler("unset", unset))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(CommandHandler("about", about))

    dispatcher.add_handler(MessageHandler(Filters.text, manage_text))
    dispatcher.add_handler(MessageHandler(Filters.command, manage_command))

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
