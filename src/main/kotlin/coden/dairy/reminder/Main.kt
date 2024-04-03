package coden.dairy.reminder

import coden.dairy.reminder.console.ConsoleTrigger
import coden.dairy.reminder.console.ConsoleUI
import coden.dairy.reminder.core.DefaultRequester
import coden.dairy.reminder.core.InMemoryRepository


fun main() {
    val ui = ConsoleUI()
    val requester =DefaultRequester(ConsoleUI(),InMemoryRepository())
    val consoleTrigger = ConsoleTrigger(requester, ui)

    consoleTrigger.start()
}

