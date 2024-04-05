package coden.journal.core.oracle

import java.time.YearMonth

interface Oracle {
    fun isPending(month: YearMonth): Boolean

    fun pending(): Iterator<YearMonth>
    fun upcoming(): Iterator<YearMonth>
}