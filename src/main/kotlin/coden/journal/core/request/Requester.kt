package coden.journal.core.request

import java.time.YearMonth

interface Requester {
    fun request(month: YearMonth)
    fun request()
}