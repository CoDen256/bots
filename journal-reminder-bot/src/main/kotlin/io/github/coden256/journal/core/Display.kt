package io.github.coden256.journal.core

import java.time.YearMonth

interface Display {
    fun displayReminder(month: YearMonth)
}