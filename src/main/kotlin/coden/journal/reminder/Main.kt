package coden.journal.reminder

import coden.journal.reminder.console.ConsoleTrigger
import coden.journal.reminder.console.ConsoleUI
import coden.journal.reminder.core.DefaultRequester
import coden.journal.reminder.core.InMemoryRepository
import coden.journal.reminder.telebot.TelegramBot
import coden.journal.reminder.telebot.TelegramBotConfiguration
import kotlinx.coroutines.runBlocking


fun main() {
    val ui = ConsoleUI()
    val requester = DefaultRequester(ConsoleUI(), InMemoryRepository())
    val consoleTrigger = ConsoleTrigger(requester, ui)

    val telegramBotTrigger = TelegramBot(
        TelegramBotConfiguration(
            "",
            5275116671
        ),
        requester
    )

    telegramBotTrigger.start()
}

