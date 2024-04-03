package coden.journal.schedule

data class ScheduleConfig(
    val cron: String,
    val enabled: Boolean
)