package io.github.coden256.journal.core.persistance

import java.time.YearMonth

interface JournalRepository {
    fun entries(): Result<Collection<JournalEntry>>

    fun get(month: YearMonth): Result<JournalEntry>

    fun first(): Result<JournalEntry>
    fun last(): Result<JournalEntry>

    fun insert(entry: JournalEntry): Result<Unit>
    fun delete(month: YearMonth): Result<Unit>

    fun clear(): Result<Long>
}