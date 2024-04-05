package coden.journal

import coden.journal.core.Display
import coden.journal.core.executor.DefaultJournalExecutor
import coden.journal.core.executor.JournalExecutor
import coden.journal.core.persistance.JournalRepository
import coden.journal.core.notify.*
import coden.journal.core.Never
import coden.journal.core.Trigger
import coden.journal.core.oracle.DefaultOracle
import coden.journal.core.oracle.Oracle
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

fun cronTrigger(schedule: ScheduleConfig, notifier: Notifier): Trigger {
    if (!schedule.enabled) return Never
    return CronTrigger(
        schedule.cron,
        Executors.newSingleThreadExecutor().asCoroutineDispatcher(),
        notifier
    )
}

fun telegramBot(telegram: TelegramBotConfig, interactor: JournalExecutor): JournalTelegramBot{
    return JournalTelegramBot(telegram, interactor)
}

fun main() {
    "s s s".split(" ", limit = 3)
    val config = config()

    val client: NotionClient = notionClient(config.notion)
    val repository: JournalRepository = notionJournalTable(client, config.notion)

    val oracle = DefaultOracle(repository)
    val interactor: JournalExecutor = DefaultJournalExecutor(repository, oracle)

    val console: JournalTelegramBot = telegramBot(config.telegram, interactor)
    val notifier: Notifier = DefaultNotifier(console, oracle)

    val trigger: Trigger = cronTrigger(config.schedule, notifier)

    console.start()
    trigger.start()
}

