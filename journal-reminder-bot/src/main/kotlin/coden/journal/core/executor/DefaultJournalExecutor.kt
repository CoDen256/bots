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
        logger.info { "Adding entry ${if (request.overwrite) "**forcefully**" else ""} for ${request.month}: ${request.description.take(10)}[...]" }
        if (!oracle.isPending(request.month) and !request.overwrite){
            return Result.failure(IllegalStateException("${request.month} is not pending, request denied. Try force overwriting it."))
        }
        val entry = JournalEntry(request.month, request.description)
        repository.insert(entry)
        return Result.success(NewEntryResponse(entry.month))
            .also { logger.info { "Adding entry: Success!" } }
    }

    override fun execute(request: NewUndatedEntryRequest): Result<NewEntryResponse> {
        logger.info { "Adding new undated entry..." }
        val pending = oracle.pending()
        if (pending.hasNext().not()){ return Result.failure(IllegalStateException("No pending journal entries to write for. Come again next month."))}
        val next = pending.next()
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
                    .also { logger.info { "Listing entries: Success!" } }
            }
    }

    override fun execute(request: RemoveDatedEntryRequest): Result<RemoveEntryResponse> {
        logger.info { "Deleting ${request.month}..." }
        repository.delete(request.month)
        return Result.success(RemoveEntryResponse(request.month))
            .also { logger.info { "Removing entry: Success!" } }

    }

    override fun execute(request: RemoveUndatedEntryRequest): Result<RemoveEntryResponse> {
        logger.info { "Deleting undated entry..." }
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
            .also { logger.info { "Clearing entries: Success!" } }

    }

    override fun execute(request: ListPendingEntryRequest): Result<PendingEntriesListResponse> {
        logger.info { "Listing all pending requests..." }
        return Result.success(
            PendingEntriesListResponse(
                oracle.pending().asSequence().toList()
            )
        )
            .also { logger.info { "Listing pending requests: Success!" } }
    }
}
