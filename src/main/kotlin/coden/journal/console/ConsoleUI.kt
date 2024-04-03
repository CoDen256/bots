package coden.journal.console

import coden.journal.core.request.UI
import java.time.YearMonth

class ConsoleUI: UI {
    override fun request(month: YearMonth) {
        print("Please add an entry for $month: ")
    }

    override fun error(throwable: Throwable) {
        println("ERROR"+throwable.message)
    }
}