package coden.journal.core.persistance

import java.time.YearMonth

interface JournalRepository {
    fun entries(): Collection<JournalEntry>

    fun get(month: YearMonth): Result<JournalEntry>

    fun first(): Result<JournalEntry>
    fun last(): Result<JournalEntry>

    fun insert(entry: JournalEntry)
    fun delete(month: YearMonth)

    fun clear()
}