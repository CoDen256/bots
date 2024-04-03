package coden.journal

import coden.journal.console.STDOUTConsoleUI
import coden.journal.core.Console
import coden.journal.core.DefaultJournalInteractor
import coden.journal.core.JournalInteractor
import coden.journal.core.persistance.JournalRepository
import coden.journal.core.request.NullTrigger
import coden.journal.core.request.Trigger
import coden.journal.core.request.UI
import coden.journal.notion.NotionConfig
import coden.journal.notion.NotionJournalTable
import coden.journal.schedule.CronTrigger
import coden.journal.schedule.ScheduleConfig
import coden.journal.telebot.JournalTelegramBot
import coden.journal.telebot.TelegramBotConfig
import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addResourceSource
import kotlinx.coroutines.asCoroutineDispatcher
import notion.api.v1.NotionClient
import notion.api.v1.logging.JavaUtilLogger
import notion.api.v1.logging.StdoutLogger
import org.apache.logging.log4j.LogManager
import java.util.concurrent.Executors


data class Config(
    val schedule: ScheduleConfig,
    val notion: NotionConfig,
    val telegram: TelegramBotConfig
)


fun config(): Config{
    return ConfigLoaderBuilder.default()
        .addResourceSource("/application.yml")
        .build()
        .loadConfigOrThrow<Config>()
}


fun notionClient(config: NotionConfig): NotionClient{
    return NotionClient(
        token = config.token,
        logger = JavaUtilLogger()
    )
}

fun notionJournalTable(client: NotionClient, config: NotionConfig): JournalRepository{
    return NotionJournalTable(client, config.db)
}

fun defaultInteractor(repository: JournalRepository, ui: UI): JournalInteractor {
    return DefaultJournalInteractor(repository, ui)
}

fun cronTrigger(schedule: ScheduleConfig, interactor: JournalInteractor): Trigger {
    return CronTrigger(
        schedule.cron,
        Executors.newSingleThreadExecutor().asCoroutineDispatcher(),
        interactor
    )
}

fun telegramBot(telegram: TelegramBotConfig, interactor: JournalInteractor): Console{
    return JournalTelegramBot(telegram, interactor)
}

fun main() {

    val config = config()

    val client = notionClient(config.notion)
    val repository = notionJournalTable(client, config.notion)

    val ui = STDOUTConsoleUI()
    val interactor = defaultInteractor(repository, ui)

    val trigger = if (config.schedule.enabled) cronTrigger(config.schedule, interactor) else NullTrigger()

    val console = telegramBot(config.telegram, interactor)


    console.start()
    trigger.start()
}

