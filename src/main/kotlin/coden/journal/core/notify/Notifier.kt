package coden.journal.core.notify

import java.time.YearMonth

interface Notifier {
    fun notify(month: YearMonth)
    fun notify()
}