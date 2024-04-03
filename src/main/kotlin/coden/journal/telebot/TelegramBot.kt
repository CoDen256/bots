package coden.journal.telebot

import coden.journal.core.persistance.JournalRepository
import coden.journal.core.persistance.JournalWriter
import coden.journal.core.request.Trigger
import coden.journal.core.request.UI
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.text
import com.github.kotlintelegrambot.entities.ChatId
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class TelegramBot(
    private val config: TelegramBotConfiguration,
    private val repository: JournalRepository,
): UI, Trigger, JournalWriter {

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

    override fun request(month: YearMonth){
        send("Sup, please add a journal entry for the $month")
    }

    private fun send(text: String) {
        bot.sendMessage(ChatId.fromId(config.target), text)
    }

    override fun error(throwable: Throwable) {
        TODO("Not yet implemented")
    }
}