package io.github.coden256.journal.core.executor

import io.github.coden256.journal.core.oracle.Oracle
import io.github.coden256.journal.core.persistance.JournalEntry
import io.github.coden256.journal.core.persistance.JournalRepository
import org.apache.logging.log4j.kotlin.Logging

class DefaultJournalExecutor(
    private val repository: JournalRepository,
    private val oracle: Oracle,
) : io.github.coden256.journal.core.executor.JournalExecutor, Logging {

    override fun execute(request: io.github.coden256.journal.core.executor.NewDatedEntryRequest): Result<io.github.coden256.journal.core.executor.NewEntryResponse> {
        logger.info { "Adding entry ${if (request.overwrite) "**forcefully**" else ""} for ${request.month}: ${request.description.take(10)}[...]" }
        if (!oracle.isPending(request.month) and !request.overwrite){
            return Result.failure(IllegalStateException("${request.month} is not pending, request denied. Try force overwriting it."))
        }
        val entry = JournalEntry(request.month, request.description)
        repository.insert(entry)
        return Result.success(io.github.coden256.journal.core.executor.NewEntryResponse(entry.month))
            .also { logger.info { "Adding entry: Success!" } }
    }

    override fun execute(request: io.github.coden256.journal.core.executor.NewUndatedEntryRequest): Result<io.github.coden256.journal.core.executor.NewEntryResponse> {
        logger.info { "Adding new undated entry..." }
        val pending = oracle.pending()
        if (pending.hasNext().not()){ return Result.failure(IllegalStateException("No pending journal entries to write for. Come again next month."))}
        val next = pending.next()
        return execute(io.github.coden256.journal.core.executor.NewDatedEntryRequest(next, request.description))
    }

    override fun execute(request: io.github.coden256.journal.core.executor.ListEntriesRequest): Result<io.github.coden256.journal.core.executor.DatedEntryListResponse> {
        logger.info { "Listing entries..." }
        return repository
            .entries()
            .map { entries ->
                io.github.coden256.journal.core.executor.DatedEntryListResponse(
                    entries.map {
                        io.github.coden256.journal.core.executor.DatedEntryResponse(
                            it.month,
                            it.description
                        )
                    }
                )
                    .also { logger.info { "Listing entries: Success!" } }
            }
    }

    override fun execute(request: io.github.coden256.journal.core.executor.RemoveDatedEntryRequest): Result<io.github.coden256.journal.core.executor.RemoveEntryResponse> {
        logger.info { "Deleting ${request.month}..." }
        repository.delete(request.month)
        return Result.success(io.github.coden256.journal.core.executor.RemoveEntryResponse(request.month))
            .also { logger.info { "Removing entry: Success!" } }

    }

    override fun execute(request: io.github.coden256.journal.core.executor.RemoveUndatedEntryRequest): Result<io.github.coden256.journal.core.executor.RemoveEntryResponse> {
        logger.info { "Deleting undated entry..." }
        return repository
            .last()
            .map { io.github.coden256.journal.core.executor.RemoveDatedEntryRequest(it.month) }
            .map { execute(it) }
            .mapCatching { it.getOrThrow() }
    }

    override fun execute(request: io.github.coden256.journal.core.executor.ClearEntriesRequest): Result<io.github.coden256.journal.core.executor.ClearEntryResponse> {
        logger.info { "Clearing all entries..." }
        return repository
            .clear()
            .map { io.github.coden256.journal.core.executor.ClearEntryResponse(it) }
            .also { logger.info { "Clearing entries: Success!" } }

    }

    override fun execute(request: io.github.coden256.journal.core.executor.ListPendingEntryRequest): Result<io.github.coden256.journal.core.executor.PendingEntriesListResponse> {
        logger.info { "Listing all pending requests..." }
        return Result.success(
            io.github.coden256.journal.core.executor.PendingEntriesListResponse(
                oracle.pending().asSequence().toList()
            )
        )
            .also { logger.info { "Listing pending requests: Success!" } }
    }
}
