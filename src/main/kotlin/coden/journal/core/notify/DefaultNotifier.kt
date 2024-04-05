package coden.journal.core.notify

import coden.journal.core.Display
import coden.journal.core.oracle.Oracle
import org.apache.logging.log4j.kotlin.Logging

class DefaultNotifier(
    private val display: Display,
    private val oracle: Oracle
) : Notifier, Logging {

    override fun check() {
        logger.info("Checking pending reminders.")
        val pending = oracle.pending()
        if (!pending.hasNext()) {
            logger.info("No pending reminders. Skip.")
            return
        }
        for (month in pending) {
            logger.info { "Notifying user for $month" }
            display.displayReminder(month)
        }
    }
}