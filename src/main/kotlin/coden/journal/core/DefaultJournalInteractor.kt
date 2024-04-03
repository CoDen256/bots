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

    override fun write(entry: JournalEntry) {
        logger.info { "Adding entry for ${entry.month}: ${entry.description.take(10)}[...]" }
        repository.insert(entry)
    }

    override fun request(month: YearMonth) {
        logger.info { "Requesting entry for $month" }
        ui.request(month)
    }

    override fun request() {
        request(YearMonth.now())
    }

    override fun list(): Collection<JournalEntry> {
        return repository.entries()
    }
}
