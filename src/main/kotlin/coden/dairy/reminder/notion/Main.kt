package coden.dairy.reminder.notion

import coden.dairy.reminder.console.ConsoleUI
import coden.dairy.reminder.core.DairyEntry
import coden.dairy.reminder.core.DairyRepository
import coden.dairy.reminder.core.DefaultRequester
import java.time.LocalDate
import java.time.YearMonth


fun main() {
    DefaultRequester(ConsoleUI(), object :DairyRepository{
        override fun entries(): Collection<DairyEntry> {
            TODO("Not yet implemented")
        }

        override fun get(month: LocalDate): Result<DairyEntry> {
            TODO("Not yet implemented")
        }

        override fun first(): Result<DairyEntry> {
            TODO("Not yet implemented")
        }

        override fun last(): Result<DairyEntry> {
            TODO("Not yet implemented")
        }

        override fun insert(entry: DairyEntry) {
            TODO("Not yet implemented")
        }

        override fun delete(month: LocalDate) {
            TODO("Not yet implemented")
        }

        override fun clear() {
            TODO("Not yet implemented")
        }
    }).triggerRequest(YearMonth.now())
}

