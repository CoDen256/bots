package coden.journal.core.request

import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

class DefaultRequester(private val ui: UI): Requester, Logging {
    override fun request(month: YearMonth) {
        logger.info { "Requesting entry for $month" }
        ui.request(month)
    }

    override fun request() {
        request(YearMonth.now())
    }
}