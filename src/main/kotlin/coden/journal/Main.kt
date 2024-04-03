package coden.journal

import coden.journal.console.ConsoleUI
import coden.journal.core.DefaultJournalInteractor
import coden.journal.memory.InMemoryRepository
import coden.journal.schedule.CronTrigger
import coden.journal.telebot.JournalTelegramBot
import coden.journal.telebot.TelegramBotConfiguration
import kotlinx.coroutines.asCoroutineDispatcher
import java.util.concurrent.Executors


fun main() {
    val repository = InMemoryRepository()

    val interactor = DefaultJournalInteractor(
        repository,
        ConsoleUI()
    )

    val trigger = CronTrigger("/5 * * * *",
        Executors.newSingleThreadExecutor().asCoroutineDispatcher(),
        interactor
        )

    trigger.start()
//    trigger.close()
//    return
    val ui = JournalTelegramBot(
        TelegramBotConfiguration(
            token = "5275116671:AAFWFE56tOCH84NfWF6TqATIFbbPWJ9WZOU",
            target = 283382228
        ),
        interactor
    )

    ui.start()
}

