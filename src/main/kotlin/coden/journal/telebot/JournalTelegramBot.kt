package coden.journal.telebot

import coden.journal.core.Console
import coden.journal.core.JournalInteractor
import coden.journal.core.persistance.JournalEntry
import coden.journal.core.request.UI
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.command
import com.github.kotlintelegrambot.dispatcher.handlers.CommandHandlerEnvironment
import com.github.kotlintelegrambot.entities.ChatId
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class JournalTelegramBot(
    private val config: TelegramBotConfig,
    private val interactor: JournalInteractor
): UI, Console {

    private val bot = bot {
        token = config.token
        dispatch {
            command("w"){ write()}
            command("write"){ write()}
            command("l"){ list()}
            command("list"){ list()}
            command("r"){ remove()}
            command("remove"){ remove()}
            command("help"){ help()}
        }
    }

    private fun CommandHandlerEnvironment.help() {
        send("Hi, \n/w, /write <YYYY-mm> <description>")
    }

    private fun CommandHandlerEnvironment.remove() {
        val args = message.text?.split(" ", limit = 2) ?: emptyList()
        if (args.size != 2) {
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


        interactor.remove(month)
        send("Entry removed.")
    }

    private fun CommandHandlerEnvironment.list() {
        val list = interactor.list().sortedBy { it.month }.map {
            "${it.month} - ${it.description}"
        }
        if (list.isEmpty()){
            send("No entries yet")
        }else {
            send(list.joinToString("\n\n"))
        }
    }

    private fun CommandHandlerEnvironment.write() {
        val args = message.text?.split(" ", limit = 3) ?: emptyList()
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

        interactor.write(JournalEntry( month, descirption))
        send("Entry added.")
    }

    override fun start() {
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

    override fun stop() {
        bot.stopPolling()
    }
}