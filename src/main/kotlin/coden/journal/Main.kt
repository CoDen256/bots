package coden.journal

import coden.journal.core.persistance.DefaultJournalInteractor
import coden.journal.core.persistance.JournalInteractor
import coden.journal.core.persistance.JournalRepository
import coden.journal.core.request.*
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

fun interactor(repository: JournalRepository): JournalInteractor {
    return DefaultJournalInteractor(repository)
}

fun requester(ui: UI): Requester {
    return DefaultRequester(ui)
}

fun cronTrigger(schedule: ScheduleConfig, requester: Requester): Trigger {
    return CronTrigger(
        schedule.cron,
        Executors.newSingleThreadExecutor().asCoroutineDispatcher(),
        requester
    )
}

fun telegramBot(telegram: TelegramBotConfig, interactor: JournalInteractor): JournalTelegramBot{
    return JournalTelegramBot(telegram, interactor)
}

fun main() {

    val config = config()

    val client = notionClient(config.notion)
    val repository = notionJournalTable(client, config.notion)

    val interactor = interactor(repository)
    val console = telegramBot(config.telegram, interactor)

    val requester = requester(console)
    val trigger = if (config.schedule.enabled) cronTrigger(config.schedule, requester) else NullTrigger()

    console.start()
    trigger.start()
}

