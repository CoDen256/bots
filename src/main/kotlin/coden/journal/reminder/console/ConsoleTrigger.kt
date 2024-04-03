package coden.journal.reminder.console

import coden.journal.reminder.core.DairyEntryRequester
import coden.journal.reminder.core.Trigger
import coden.journal.reminder.core.UI
import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

// ideally Spring shell
class ConsoleTrigger(
    private val requester: DairyEntryRequester,
    private val ui: UI
): Trigger, Logging {

    override fun start() {
        logger.info { "Starting console" }
        while (true){
            try {
                val run = readCommand()
                if (!run){break}
            }catch (e: Exception){
                println("Error: "+e.message)
            }
        }
    }

    private fun readCommand(): Boolean {
        println("")
        println("[trigger [YYYY-mm]] - triggers")
        println("[exit] - exists")
        print("> ")
        val command = readlnOrNull()
        if (command.isNullOrBlank()) {
            println("Command must be not be blank")
            return true
        }
        val args = command.split(" ")
        if (args[0].contains("trigger")) {
            if (args.size == 2){
                val month = YearMonth.parse(args[1])
                triggerRequest(month)
            }else{
                triggerRequest(YearMonth.now())
            }
        }

        return !args[0].contains("exit")
    }

    private fun triggerRequest(month: YearMonth){
        logger.info { "Triggering for $month" }
        try {
            requester.triggerRequest(month)
        } catch (e: Exception) {
            logger.error("Error while triggering occurred", e) // for debugging
            ui.error(e)                                             // for user
        }
    }

}