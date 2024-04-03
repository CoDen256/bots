package coden.journal.core.persistance

import org.apache.logging.log4j.kotlin.Logging
import java.time.YearMonth

class DefaultJournalInteractor(
    private val repository: JournalRepository,
):
    JournalInteractor, Logging {

    override fun write(entry: JournalEntry) {
        logger.info { "Adding entry for ${entry.month}: ${entry.description.take(10)}[...]" }
        repository.insert(entry)
    }


    override fun list(): Collection<JournalEntry> {
        logger.info { "Listing entries..." }
        return repository.entries()
    }

    override fun remove(month: YearMonth) {
        logger.info { "Deleting $month..." }
        repository.delete(month)
    }
}
