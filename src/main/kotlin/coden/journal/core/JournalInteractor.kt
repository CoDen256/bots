package coden.journal.core

import java.time.Month
import java.time.YearMonth

interface JournalInteractor {
    fun write(month: YearMonth, description: String)
}