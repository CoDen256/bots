package coden.journal.core.oracle

import coden.journal.core.persistance.JournalRepository
import java.time.YearMonth

class DefaultOracle(
    private val repository: JournalRepository
): Oracle {
    override fun shouldNotify(): Boolean {
        return shouldNotify(YearMonth.now())
    }

    override fun shouldNotify(month: YearMonth): Boolean {
        return true
    }
}