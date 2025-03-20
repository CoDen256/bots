package coden.journal.core.oracle

import coden.journal.core.persistance.JournalRepository
import java.time.LocalDate
import java.time.Month
import java.time.Year
import java.time.YearMonth

class DefaultOracle(
    private val start: YearMonth,
    private val offset: Long,
    private val repository: JournalRepository
) : Oracle {

    override fun isPending(month: YearMonth): Boolean {
        return pending().asSequence().contains(month)
    }

    override fun pending(): Iterator<YearMonth> {
        val months: Sequence<YearMonth> = months(start, current())
        val entries = repository.entries().getOrNull()?.map { it.month } ?: return months.iterator()

        return months
            .filter { !entries.contains(it) }
            .iterator()
    }

    override fun upcoming(): Iterator<YearMonth> {
        return months(next(), YearMonth.of(Year.MAX_VALUE, Month.DECEMBER)).iterator()
    }

    private fun current(): YearMonth {
        return YearMonth.from(LocalDate.now().plusDays(offset))
    }
    private fun next(): YearMonth = current().plusMonths(1)
}

/**
 * [start] - inclusive
 * [until] - inclusive
 */
fun months(start: YearMonth, until: YearMonth): Sequence<YearMonth> {
    return generateSequence(start) { it.plusMonths(1) }
        .takeWhile { !it.isAfter(until) }
}