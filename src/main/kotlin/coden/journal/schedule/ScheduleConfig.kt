package coden.journal.schedule

data class ScheduleConfig(
    private val cron: String,
    private val enabled: Boolean
) {
}