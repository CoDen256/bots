package io.github.coden256.journal

import io.github.coden256.journal.core.Never
import io.github.coden256.journal.core.Trigger
import io.github.coden256.journal.core.executor.DefaultJournalExecutor
import io.github.coden256.journal.core.executor.JournalExecutor
import io.github.coden256.journal.core.notify.DefaultNotifier
import io.github.coden256.journal.core.notify.Notifier
import io.github.coden256.journal.core.oracle.DefaultOracle
import io.github.coden256.journal.core.oracle.OracleConfig
import io.github.coden256.journal.core.persistance.JournalRepository
import io.github.coden256.journal.notion.NotionConfig
import io.github.coden256.journal.notion.NotionJournalTable
import io.github.coden256.journal.schedule.CronTrigger
import io.github.coden256.journal.schedule.ScheduleConfig
import io.github.coden256.journal.telebot.JournalTelegramBot
import io.github.coden256.journal.telebot.TelegramBotConfig
import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addFileSource
import com.sksamuel.hoplite.addResourceSource
import kotlinx.coroutines.asCoroutineDispatcher
import notion.api.v1.NotionClient
import notion.api.v1.http.OkHttp4Client
import notion.api.v1.logging.JavaUtilLogger
import java.util.concurrent.Executors


data class Config(
    val oracle: OracleConfig,
    val schedule: ScheduleConfig,
    val notion: NotionConfig,
    val telegram: TelegramBotConfig
)


fun config(): Config{
    return ConfigLoaderBuilder.default()
        .addResourceSource("/application.yml", optional = true)
        .addFileSource("application.yml", optional = true)
        .build()
        .loadConfigOrThrow<Config>()
}


fun notionClient(config: NotionConfig): NotionClient{
    return NotionClient(
        token = config.token,
        httpClient =  OkHttp4Client(
            connectTimeoutMillis = 3 * 1000,
            readTimeoutMillis = 10 * 1000,
            writeTimeoutMillis = 10 * 1000
        ),
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
    val config = config()

    val client: NotionClient = notionClient(config.notion)
    val repository: JournalRepository = notionJournalTable(client, config.notion)

    val oracle = DefaultOracle(config.oracle.start, config.oracle.offset, repository)

    val interactor: JournalExecutor =
        DefaultJournalExecutor(repository, oracle)

    val console: JournalTelegramBot = telegramBot(config.telegram, interactor)
    val notifier: Notifier = DefaultNotifier(console, oracle)

    val trigger: Trigger = cronTrigger(config.schedule, notifier)

    console.start()
    trigger.start()
}

