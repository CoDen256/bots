package coden.journal.core

import coden.journal.core.persistance.JournalEntry
import java.time.YearMonth

interface JournalInteractor {
    fun write(entry: JournalEntry)
    fun request(month: YearMonth)
    fun list(): Collection<JournalEntry>
    fun remove(month: YearMonth)
    fun request()
}