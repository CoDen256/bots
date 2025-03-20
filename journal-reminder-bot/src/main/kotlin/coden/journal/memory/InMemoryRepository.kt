package coden.journal.memory

import coden.journal.core.persistance.JournalEntry
import coden.journal.core.persistance.JournalRepository
import java.time.YearMonth

class InMemoryRepository: JournalRepository {

    private val entities: MutableMap<YearMonth, JournalEntry> = HashMap()

    override fun entries(): Result<Collection<JournalEntry>> {
        return Result.success(entities.values)
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

    override fun insert(entry: JournalEntry): Result<Unit> {
        entities[entry.month] = entry
        return Result.success(Unit)
    }

    override fun delete(month: YearMonth): Result<Unit> {
        entities.remove(month)
        return Result.success(Unit)
    }

    override fun clear(): Result<Long> {
        val value = entities.size.toLong()
        entities.clear()
        return Result.success(value)
    }
}