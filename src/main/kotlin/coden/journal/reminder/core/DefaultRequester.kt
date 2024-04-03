package coden.journal.reminder.core

import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

class DefaultRequester(
    private val ui: UI,
    private val repository: DairyRepository
) : DairyEntryRequester, Logging {

    override fun triggerRequest(month: YearMonth) {
        logger.info { "Requesting user dairy entry for $month..." }
        val entry = ui.requestEntry(month).getOrThrow()
        logger.info { "New Entry: ${entry.take(20)} [...] \nInserting..." }
        repository.insert(DairyEntry(month.atDay(1), entry))
        logger.info { "Successfully inserted for $month" }
    }

}