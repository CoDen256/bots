package coden.journal.reminder.core

import java.time.YearMonth

interface DairyEntryRequester {
    fun triggerRequest(month: YearMonth)
}