package coden.journal.core.executor

import java.time.YearMonth

interface JournalExecutor {
    fun execute(request: NewDatedEntryRequest)
    fun execute(request: NewUndatedEntryRequest)

    fun execute(request: ListEntriesRequest): DatedEntryListResponse

    fun execute(request: RemoveDatedEntryRequest)
    fun execute(request: RemoveUndatedEntryRequest)

    fun execute(request: ClearEntriesRequest)
}

interface JournalRequest

object ListEntriesRequest: JournalRequest

data class NewDatedEntryRequest(
    val month: YearMonth,
    val description: String
): JournalRequest

data class NewUndatedEntryRequest(
    val description: String
): JournalRequest

data class RemoveDatedEntryRequest(
    val month: YearMonth
): JournalRequest

object RemoveUndatedEntryRequest : JournalRequest

object ClearEntriesRequest :JournalRequest


interface JournalResponse

data class DatedEntryResponse(
    val month: YearMonth,
    val description: String
): JournalResponse

data class DatedEntryListResponse(
    val entries: List<DatedEntryResponse>
): JournalResponse
