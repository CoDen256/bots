package io.github.coden256.journal.schedule

data class ScheduleConfig(
    val cron: String,
    val enabled: Boolean
)