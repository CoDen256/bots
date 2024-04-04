package coden.journal.core.executor

import coden.journal.core.oracle.Oracle
import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import org.apache.logging.log4j.kotlin.Logging

class DefaultJournalExecutor(
    private val repository: JournalRepository,
    private val oracle: Oracle,
) : JournalExecutor, Logging {

    override fun execute(request: NewDatedEntryRequest) {
        logger.info { "Adding entry for ${request.month}: ${request.description.take(10)}[...]" }
        repository.insert(JournalEntry(request.month, request.description))
    }

    override fun execute(request: NewUndatedEntryRequest) {
        TODO("Not yet implemented")
    }

    override fun execute(request: ListEntriesRequest): DatedEntryListResponse {
        logger.info { "Listing entries..." }
        return DatedEntryListResponse(
            repository
                .entries()
                .map { DatedEntryResponse(it.month, it.description) }
        )
    }

    override fun execute(request: RemoveDatedEntryRequest) {
        logger.info { "Deleting ${request.month}..." }
        repository.delete(request.month)
    }

    override fun execute(request: RemoveUndatedEntryRequest) {
        TODO("Not yet implemented")
    }

    override fun execute(request: ClearEntriesRequest) {
        TODO("Not yet implemented")
    }
}
