package coden.dairy.reminder.model

import java.time.LocalDate

interface DairyRepository {
    fun entries(): Collection<DairyEntry>

    fun get(index: Int): DairyEntry
    fun first(): DairyEntry
    fun last(): DairyEntry

    fun insert(entry: DairyEntry)
    fun delete(index: Int)

    fun clear()
}

data class DairyEntry(
    val month: LocalDate,
    val description: String,
)