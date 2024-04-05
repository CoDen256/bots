package coden.journal.telebot

import coden.journal.core.Display
import coden.journal.core.ExecutorConsole
import coden.journal.core.executor.*
import com.github.kotlintelegrambot.bot
import com.github.kotlintelegrambot.dispatch
import com.github.kotlintelegrambot.dispatcher.command
import com.github.kotlintelegrambot.dispatcher.message
import com.github.kotlintelegrambot.entities.ChatId
import com.github.kotlintelegrambot.entities.Message
import com.github.kotlintelegrambot.extensions.filters.Filter
import org.apache.logging.log4j.kotlin.logger
import java.time.YearMonth

class JournalTelegramBot(
    private val config: TelegramBotConfig,
    private val executor: JournalExecutor
): Display, ExecutorConsole {

    private val bot = bot {
        token = config.token
        dispatch {
            message(Filter.Command.not().and(Filter.Text)) {
                val origin = message.text
                write(message.copy(text = "/w $origin"))
            }
            command("w"){ notifyOnError { write(message)}}
            command("write"){ notifyOnError { write(message)}}
            command("force"){ notifyOnError { write(message)}}
            command("l"){ notifyOnError { list(message)}}
            command("list"){ notifyOnError { list(message)}}
            command("r"){ notifyOnError { remove(message)}}
            command("remove"){ notifyOnError { remove(message)}}
            command("c"){ notifyOnError { clear(message)}}
            command("clear"){ notifyOnError { clear(message)}}
            command("p"){ notifyOnError { pending(message)}}
            command("pending"){ notifyOnError { pending(message)}}
            command("help"){ notifyOnError { help(message)}}
        }
    }

    private fun notifyOnError(handler: () -> Unit){
        try {
            handler()
        }catch (e: Exception){
            send("Error: ${e.message}")
        }
    }

    private fun help(message: Message) {
        send("Hi, " +
                "\n/h, /help" +
                "\n/r, /remove <YYYY-mm>" +
                "\n/r, /remove" +
                "\n/w, /write <YYYY-mm> <description>" +
                "\n/w, /write <description>" +
                ""
        )
    }

    private fun remove(message: Message) {
        val args = args(message, 1)
            .recoverCatching { args(message,0).getOrThrow() }
            .onFailure { send(it.message) }
            .getOrNull() ?: return

        if (args.size == 1){
            val month = parseMonth(args[0])
                .onFailure { send(it.message) }
                .getOrNull() ?: return

            executor.execute(RemoveDatedEntryRequest(month))
                .onSuccess { send("Entry for <${it.month}> is removed.") }
                .onFailure { send("Failed to remove entry: ${it.message}") }
        }else {
            executor.execute(RemoveUndatedEntryRequest)
                .onSuccess { send("Entry for <${it.month}> is removed.") }
                .onFailure { send("Failed to remove entry: ${it.message}") }
        }

    }

    private fun args(message: Message, arity: Int): Result<List<String>> {
        val args = message.text?.split(" ", limit = arity + 1) ?: emptyList()
        if (args.size != arity + 1) {
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

    private fun list(message: Message) {
        val list = executor
            .execute(ListEntriesRequest)
            .onFailure { send("Unable to retrieve entries: ${it.message}") }
            .getOrNull()
            ?.entries
            ?.sortedBy { it.month }
            ?.map { format(it) }
            ?: return

        if (list.isEmpty()){
            send("No entries yet.")
        }else {
            send(list.joinToString("\n\n"))
        }
    }

    private fun pending(message: Message) {
        val list = executor
            .execute(ListPendingEntryRequest)
            .onFailure { send("Unable to retrieve entries: ${it.message}") }
            .getOrNull()
            ?.months
            ?.sortedBy { it.month }
            ?.map { it.toString() }
            ?: return

        if (list.isEmpty()){
            send("No pending requests yet.")
        }else {
            send(list.joinToString("\n\n"))
        }
    }

    private fun clear(message: Message) {
        val cleared = executor
            .execute(ClearEntriesRequest)
            .onFailure { send("Unable to clear entries: ${it.message}") }
            .getOrNull()
            ?.count
            ?: return

        send("($cleared) entries cleared.")
    }

    private fun format(it: DatedEntryResponse) = "${it.month} - ${it.description}"

    private fun write(message: Message) {
        val force = message.text?.startsWith("/force") ?: false
        val monthPresent = isMonthPresent(message)

        if (monthPresent){
            val args = args(message,2)
                .onFailure { send(it.message) }
                .getOrNull() ?: return

            val month = parseMonth(args[0])
                .onFailure { send(it.message) }
                .getOrNull() ?: return

            val description = args[1]
            executor.execute(NewDatedEntryRequest(month, description, force))
                .onSuccess { send("Entry for ${it.month} is written") }
                .onFailure { send("Failed to write entry: ${it.message}") }
        }
        else{
            val args = args(message, 1)
                .onFailure { send(it.message) }
                .getOrNull() ?: return

            val description = args[0]
            executor.execute(NewUndatedEntryRequest(description))
                .onSuccess { send("Entry for ${it.month} is written") }
                .onFailure { send("Failed to write entry: ${it.message}") }
        }
    }

    private fun isMonthPresent(message: Message): Boolean {
        val args = message.text?.split(" ", limit = 3) ?: return false
        if (args.size <= 2){ return false }
        return args[1].matches(Regex("\\d\\d\\d\\d-\\d\\d"))
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