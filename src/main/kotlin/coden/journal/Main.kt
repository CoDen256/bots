package coden.journal

import coden.journal.core.DefaultJournalInteractor
import coden.journal.memory.InMemoryRepository
import coden.journal.telebot.JournalTelegramBot
import coden.journal.telebot.TelegramBotConfiguration


fun main() {
    val repository = InMemoryRepository()

    val interactor = DefaultJournalInteractor(repository)

    val ui = JournalTelegramBot(
        TelegramBotConfiguration(
            token = "5275116671:AAFWFE56tOCH84NfWF6TqATIFbbPWJ9WZOU",
            target = 5275116671L
        ),
        interactor
    )

    ui.start()
}

