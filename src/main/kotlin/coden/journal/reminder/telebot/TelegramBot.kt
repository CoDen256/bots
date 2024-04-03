package coden.journal.reminder.telebot

import coden.journal.reminder.core.DairyEntryRequester
import coden.journal.reminder.core.Trigger
import coden.journal.reminder.core.UI
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.text
import com.github.kotlintelegrambot.entities.ChatId
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class TelegramBot(
    private val config: TelegramBotConfiguration,
    private val requester: DairyEntryRequester
): UI, Trigger {

    private val bot = bot {
        token = config.token
        dispatch {
            this.
            text {
                bot.sendMessage(ChatId.fromId(message.chat.id), text = text)
            }
        }
    }

    override fun start() {
        logger.info { "Admin: ${bot.getMe().getOrNull()?.id}" }
        logger.info { "Start polling for ${config.target} " }
        send("Hi! This is Dairy reminder bot. Im gonna remind you to journal regularly")
        bot.startPolling()
    }

    override fun requestEntry(month: YearMonth): Result<String> {
        send("Hi")
    }

    private fun send(text: String) {
        bot.sendMessage(ChatId.fromId(config.target), text)
    }

    override fun error(throwable: Throwable) {
        TODO("Not yet implemented")
    }
}