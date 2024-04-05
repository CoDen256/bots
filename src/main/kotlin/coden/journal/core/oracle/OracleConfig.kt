package coden.journal.core.oracle

import java.time.YearMonth

data class OracleConfig(
    val start: YearMonth,
    val offset: Long,
)
