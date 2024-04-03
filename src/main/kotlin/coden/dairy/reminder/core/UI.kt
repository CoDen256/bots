package coden.dairy.reminder.core

import java.time.YearMonth

interface UI {
    fun requestEntry(month: YearMonth): Result<String>
}