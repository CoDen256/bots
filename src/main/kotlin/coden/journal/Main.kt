package coden.journal

import coden.journal.console.STDOUTConsoleUI
import coden.journal.core.DefaultJournalInteractor
import coden.journal.notion.NotionConfig
import coden.journal.notion.NotionJournalTable
import coden.journal.schedule.ScheduleConfig
import coden.journal.telebot.JournalTelegramBot
import coden.journal.telebot.TelegramBotConfig
import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addResourceSource
import notion.api.v1.NotionClient


data class Config(
    val schedule: ScheduleConfig,
    val notion: NotionConfig,
    val telegram: TelegramBotConfig
)

fun main() {
    val config = ConfigLoaderBuilder.default()
        .addResourceSource("/application.yml")
        .build()
        .loadConfigOrThrow<Config>()

    val client = NotionClient(
        token = "secret_wxvtjYJCvMC2r4kzlNCtYaT9MfJTiboXx3Yqn9jBHkO"
    )
    val repository = NotionJournalTable(
        client, "190f84868e7b4af7ab17a16493c0a5e2"
    )

    val interactor = DefaultJournalInteractor(
        repository,
        STDOUTConsoleUI()
    )

//    val trigger = CronTrigger("/5 * * * *",
//        Executors.newSingleThreadExecutor().asCoroutineDispatcher(),
//        interactor
//        )
//
//    trigger.start()
//    trigger.close()
//    return
    val ui = JournalTelegramBot(
        TelegramBotConfig(
            token = "5275116671:AAFWFE56tOCH84NfWF6TqATIFbbPWJ9WZOU",
            target = 283382228
        ),
        interactor
    )

    ui.start()
}

