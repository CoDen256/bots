package coden.journal.core.executor

import java.time.YearMonth

interface JournalExecutor {
    fun execute(request: NewDatedEntryRequest): Result<NewEntryResponse>
    fun execute(request: NewUndatedEntryRequest): Result<NewEntryResponse>

    fun execute(request: ListEntriesRequest): Result<DatedEntryListResponse>

    fun execute(request: RemoveDatedEntryRequest): Result<RemoveEntryResponse>
    fun execute(request: RemoveUndatedEntryRequest): Result<RemoveEntryResponse>

    fun execute(request: ClearEntriesRequest): Result<ClearEntryResponse>
    fun execute(request: ListPendingEntryRequest): Result<PendingEntriesListResponse>
}


sealed interface JournalRequest

data object ListEntriesRequest: JournalRequest

data class NewDatedEntryRequest(
    val month: YearMonth,
    val description: String,
    val overwrite: Boolean = false
): JournalRequest

data class NewUndatedEntryRequest(
    val description: String
): JournalRequest

data class RemoveDatedEntryRequest(
    val month: YearMonth
): JournalRequest

data object RemoveUndatedEntryRequest : JournalRequest

data object ClearEntriesRequest :JournalRequest

data object ListPendingEntryRequest: JournalRequest

interface JournalResponse

data class DatedEntryResponse(
    val month: YearMonth,
    val description: String
): JournalResponse

data class DatedEntryListResponse(
    val entries: List<DatedEntryResponse>
): JournalResponse


data class RemoveEntryResponse(
    val month: YearMonth
): JournalResponse

data class NewEntryResponse(
    val month: YearMonth
): JournalResponse

data class ClearEntryResponse(
    val count: Long
): JournalResponse

data class PendingEntriesListResponse (
    val months: List<YearMonth>
): JournalResponse