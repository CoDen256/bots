package coden.journal.telebot

import coden.journal.core.ExecutorConsole
import coden.journal.core.Display
import coden.journal.core.executor.*
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.command
import com.github.kotlintelegrambot.dispatcher.handlers.CommandHandlerEnvironment
import com.github.kotlintelegrambot.entities.ChatId
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class JournalTelegramBot(
    private val config: TelegramBotConfig,
    private val executor: JournalExecutor
): Display, ExecutorConsole {

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
        send("Hi, " +
                "\n/h, /help" +
                "\n/r, /remove <YYYY-mm>" +
                "\n/r, /remove" +
                "\n/w, /write <YYYY-mm> <description>" +
                "\n/w, /write <description>" +
                ""
        )
    }

    private fun CommandHandlerEnvironment.remove() {
        val args = args(1)
            .onFailure{ send(it.message) }
            .getOrNull() ?: return

        val month = parseMonth(args[0])
            .onFailure { send(it.message) }
            .getOrNull() ?: return

        executor.execute(RemoveDatedEntryRequest(month))
        send("Entry for <$month> is removed.")
    }

    private fun CommandHandlerEnvironment.args(arity: Int): Result<List<String>> {
        val args = message.text?.split(" ", limit = arity + 1) ?: emptyList()
        if (args.size != arity) {
            return Result.failure(wrongArity(arity, args))
        }
        return Result.success(args.drop(1))
    }

    private fun wrongArity(arity: Int, args: List<String>): IllegalArgumentException {
       return IllegalArgumentException("Wrong format of the command, expected $arity arguments, but was ${args.size}.")
    }

    private fun parseMonth(arg: String): Result<YearMonth> {
        return try {
            Result.success(YearMonth.parse(arg))
        } catch (e: Exception) {
            Result.failure(IllegalArgumentException("Wrong YYYY-mm format for '$arg': $e"))
        }
    }

    private fun CommandHandlerEnvironment.list() {

        val list = executor
            .execute(ListEntriesRequest)
            .entries
            .sortedBy { it.month }
            .map { format(it) }

        if (list.isEmpty()){
            send("No entries yet.")
        }else {
            send(list.joinToString("\n\n"))
        }
    }

    private fun format(it: DatedEntryResponse) = "${it.month} - ${it.description}"

    private fun CommandHandlerEnvironment.write() {
        val args = args(2)
            .recoverCatching { args(1).getOrThrow() }
            .onFailure { send(it.message) }
            .getOrNull() ?: return


        if (args.size == 2){
            val month = parseMonth(args[0])
                .onFailure { send(it.message) }
                .getOrNull() ?: return

            val description = args[1]
            executor.execute(NewDatedEntryRequest(month, description))
        }else {
            val description = args[0]
            executor.execute(NewUndatedEntryRequest(description))
        }
        send("Entry added.")
    }

    override fun start() {
        logger.info { "Start polling for ${config.target} " }
        send("Hi! This is Dairy reminder bot. Im gonna remind you to journal regularly")
        bot.startPolling()
    }

    override fun displayReminder(month: YearMonth){
        send("Sup, please add a journal entry for the $month")
    }

    private fun send(text: String?) {
        bot.sendMessage(ChatId.fromId(config.target), text ?: "<unknown error: message is empty>")
    }

    override fun stop() {
        bot.stopPolling()
    }
}