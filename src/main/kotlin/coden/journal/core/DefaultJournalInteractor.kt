package coden.journal.core

import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import coden.journal.core.request.UI
import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

class DefaultJournalInteractor(
    private val repository: JournalRepository,
    private val ui: UI,
):
    JournalInteractor, Logging {

    override fun write(month: YearMonth, description: String) {
        logger.info { "Adding entry for $month: ${description.take(10)}[...]" }
        repository.insert(JournalEntry(month, description))
    }

    override fun request(month: YearMonth) {
        logger.info { "Requesting entry for $month" }
        ui.request(month)
    }

    override fun request() {
        request(YearMonth.now())
    }

}
