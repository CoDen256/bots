package coden.journal.reminder.console

import coden.journal.reminder.core.UI
import java.time.YearMonth

class ConsoleUI: UI {
    override fun requestEntry(month: YearMonth): Result<String> {
        var entry: String?
        do {
            print("Please add an entry for $month: ")
            entry = readlnOrNull()
            if (entry.isNullOrBlank()){ println("Entry must be not blank") }

        }while (entry.isNullOrBlank())

        return Result.success(entry)
    }

    override fun error(throwable: Throwable) {
        println("ERROR"+throwable.message)
    }
}