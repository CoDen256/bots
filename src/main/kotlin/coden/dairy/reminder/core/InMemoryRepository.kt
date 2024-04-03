package coden.dairy.reminder.core

import java.time.LocalDate

class InMemoryRepository: DairyRepository {

    private val entities: MutableMap<LocalDate, DairyEntry> = HashMap()

    override fun entries(): Collection<DairyEntry> {
        return entities.values
    }

    override fun get(month: LocalDate): Result<DairyEntry> {
        return entities[month]?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entry for $month"))
    }

    override fun first(): Result<DairyEntry> {
        return entities.maxByOrNull { it.key }?.value?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun last(): Result<DairyEntry> {
        return entities.minByOrNull { it.key }?.value?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun insert(entry: DairyEntry) {
        entities[entry.month] = entry
    }

    override fun delete(month: LocalDate) {
        entities.remove(month)
    }

    override fun clear() {
        entities.clear()
    }
}