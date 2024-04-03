package coden.journal.core

import java.time.YearMonth

interface JournalInteractor {
    fun write(month: YearMonth, description: String)
    fun request(month: YearMonth)
    fun request()
}