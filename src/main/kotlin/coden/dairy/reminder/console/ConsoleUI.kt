package coden.dairy.reminder.console

import coden.dairy.reminder.core.UI
import java.time.YearMonth

class ConsoleUI: UI{
    override fun requestEntry(month: YearMonth): Result<String> {
        var entry: String?
        do {
            print("Please add an entry for $month:... ")
            entry = readlnOrNull()
            if (entry.isNullOrBlank()){ println("Entry must be not blank") }

        }while (entry.isNullOrBlank())

        return Result.success(entry)
    }
}