package coden.journal.telebot

import coden.journal.core.JournalInteractor
import coden.journal.core.request.UI
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.command
import com.github.kotlintelegrambot.dispatcher.handlers.CommandHandlerEnvironment
import com.github.kotlintelegrambot.entities.ChatId
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class JournalTelegramBot(
    private val config: TelegramBotConfiguration,
    private val interactor: JournalInteractor
): UI {

    private val bot = bot {
        token = config.token
        dispatch {
            command("w"){ write()}
            command("write"){ write()}
            command("help"){ help()}
        }
    }

    private fun CommandHandlerEnvironment.help() {
        send("Hi, \n/w, /write <YYYY-mm> <description>")
    }
    private fun CommandHandlerEnvironment.write() {
        val args = message.text?.split(" ") ?: emptyList()
        if (args.size != 3) {
            send("Wrong format")
            return
        }
        val month: YearMonth?
        try {
            month = YearMonth.parse(args.get(1))
        } catch (e: Exception) {
            send("Wrong month format" + e)
            return
        }
        val descirption = args.get(2)

        interactor.write(month, descirption)
        send("Entry added.")
    }

    fun start() {
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
}