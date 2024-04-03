package coden.dairy.reminder.model

import java.time.LocalDate

interface DairyRepository {
    fun entries(): Collection<DairyEntry>

    fun get(month: LocalDate): Result<DairyEntry>

    fun first(): Result<DairyEntry>
    fun last(): Result<DairyEntry>

    fun insert(entry: DairyEntry)
    fun delete(month: LocalDate)

    fun clear()
}

data class DairyEntry(
    val month: LocalDate,
    val description: String,
)