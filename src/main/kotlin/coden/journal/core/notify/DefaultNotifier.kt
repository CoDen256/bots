package coden.journal.core.notify

import coden.journal.core.oracle.Oracle
import coden.journal.core.Display
import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

class DefaultNotifier(
    private val display: Display,
    private val oracle: Oracle
): Notifier, Logging {

    override fun notify(month: YearMonth) {
        logger.info("Checking reminder for $month...")
        if (!oracle.shouldNotify(month)){
            logger.info("Not needed, skip.")
            return
        }
        logger.info { "Notifying user for $month" }
        display.displayReminder(month)
    }

//    override fun notify() {
//        notify(YearMonth.now())
//    }
}