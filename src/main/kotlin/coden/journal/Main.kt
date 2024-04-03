package coden.journal

import coden.journal.console.Console
import coden.journal.console.ConsoleUI
import coden.journal.memory.InMemoryRepository


fun main() {
    val ui = ConsoleUI()
    val trigger = Console(ui, InMemoryRepository())
//    val requester = DefaultUI(ConsoleUI(), InMemoryRepository())
//    val console = Console(requester, ui)



//    val telegramBotTrigger = TelegramBot(
//        TelegramBotConfiguration(
//            "",
//            5275116671
//        ),
//        requester
//    )

    trigger.start()
}

