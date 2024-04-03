package coden.journal.core.persistance

import coden.journal.core.persistance.JournalEntry
import java.time.YearMonth

interface JournalInteractor {
    fun write(entry: JournalEntry)
    fun list(): Collection<JournalEntry>
    fun remove(month: YearMonth)
}