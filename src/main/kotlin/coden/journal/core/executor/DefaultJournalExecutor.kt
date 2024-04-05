package coden.journal.core.executor

import coden.journal.core.oracle.Oracle
import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import org.apache.logging.log4j.kotlin.Logging

class DefaultJournalExecutor(
    private val repository: JournalRepository,
    private val oracle: Oracle,
) : JournalExecutor, Logging {

    override fun execute(request: NewDatedEntryRequest): Result<NewEntryResponse> {
        logger.info { "Adding entry for ${request.month}: ${request.description.take(10)}[...]" }
        val entry = JournalEntry(request.month, request.description)
        repository.insert(entry)
        return Result.success(NewEntryResponse(entry.month))
    }

    override fun execute(request: NewUndatedEntryRequest): Result<NewEntryResponse> {
        val next = oracle.pending().next()
        return execute(NewDatedEntryRequest(next, request.description))
    }

    override fun execute(request: ListEntriesRequest): Result<DatedEntryListResponse> {
        logger.info { "Listing entries..." }
        return repository
            .entries()
            .map { entries ->
                DatedEntryListResponse(
                    entries.map { DatedEntryResponse(it.month, it.description) }
                )
            }
    }

    override fun execute(request: RemoveDatedEntryRequest): Result<RemoveEntryResponse> {
        logger.info { "Deleting ${request.month}..." }
        repository.delete(request.month)
        return Result.success(RemoveEntryResponse(request.month))
    }

    override fun execute(request: RemoveUndatedEntryRequest): Result<RemoveEntryResponse> {
        return repository
            .last()
            .map { RemoveDatedEntryRequest(it.month) }
            .map { execute(it) }
            .mapCatching { it.getOrThrow() }
    }

    override fun execute(request: ClearEntriesRequest): Result<ClearEntryResponse> {
        logger.info { "Clearing all entries..." }
        return repository
            .clear()
            .map { ClearEntryResponse(it) }
    }
}
