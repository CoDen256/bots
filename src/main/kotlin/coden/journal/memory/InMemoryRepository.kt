package coden.journal.memory

import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import java.time.LocalDate
import java.time.YearMonth

class InMemoryRepository: JournalRepository {

    private val entities: MutableMap<YearMonth, JournalEntry> = HashMap()

    override fun entries(): Collection<JournalEntry> {
        return entities.values
    }

    override fun get(month: YearMonth): Result<JournalEntry> {
        return entities[month]?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entry for $month"))
    }

    override fun first(): Result<JournalEntry> {
        return entities.maxByOrNull { it.key }?.value?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun last(): Result<JournalEntry> {
        return entities.minByOrNull { it.key }?.value?.let {
            Result.success(it)
        } ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun insert(entry: JournalEntry) {
        entities[entry.month] = entry
    }

    override fun delete(month: YearMonth) {
        entities.remove(month)
    }

    override fun clear() {
        entities.clear()
    }
}