package coden.journal.reminder.core

import java.time.YearMonth

interface UI {
    fun requestEntry(month: YearMonth): Result<String>
    fun error(throwable: Throwable)
}