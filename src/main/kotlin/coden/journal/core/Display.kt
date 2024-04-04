package coden.journal.core

import java.time.YearMonth

interface Display {
    fun displayReminder(month: YearMonth)
}