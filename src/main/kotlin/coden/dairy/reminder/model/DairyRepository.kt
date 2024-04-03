package coden.dairy.reminder.model

import java.time.LocalDate
import java.util.stream.Stream

interface DairyRepository {
    fun entries(): Stream<DairyEntry>

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