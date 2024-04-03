package coden.journal.core.request

import java.time.YearMonth

interface UI {
    fun request(month: YearMonth)
    fun error(throwable: Throwable)
}