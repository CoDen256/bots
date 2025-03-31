package io.github.coden256.journal.core.persistance

import java.time.YearMonth

data class JournalEntry(
    val month: YearMonth,
    val description: String,
)