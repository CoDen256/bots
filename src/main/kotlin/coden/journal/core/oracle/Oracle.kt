package coden.journal.core.oracle

import java.time.YearMonth

interface Oracle {
    fun shouldNotify(): Boolean
    fun shouldNotify(month: YearMonth): Boolean
}