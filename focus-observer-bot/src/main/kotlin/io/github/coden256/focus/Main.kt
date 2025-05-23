package io.github.coden256.focus

import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addFileSource
import com.sksamuel.hoplite.addResourceSource
import io.github.coden256.database.database
import io.github.coden256.focus.core.impl.DefaultActionDefiner
import io.github.coden256.focus.core.impl.DefaultAttentionGiver
import io.github.coden256.focus.core.impl.DefaultFocusableAnalyser
import io.github.coden256.focus.core.impl.DefaultFocusableDefiner
import io.github.coden256.focus.core.model.FocusableRepository
import io.github.coden256.focus.postgres.PostgresFocusableRepository
import io.github.coden256.focus.postgres.RepositoryConfig
import io.github.coden256.focus.telegram.FocusObserverBot
import io.github.coden256.focus.telegram.FocusObserverDB
import io.github.coden256.focus.telegram.format.DefaultFocusableFormatter
import io.github.coden256.focus.telegram.format.FormatterConfig
import io.github.coden256.telegram.abilities.TelegramBotConfig
import io.github.coden256.telegram.run.TelegramBotConsole


data class Config(
    val telegram: TelegramBotConfig,
    val repo: RepositoryConfig,
    val format: FormatterConfig
)

fun config(): Config {
    return ConfigLoaderBuilder.default()
        .addFileSource("application.yml", optional = true)
        .addResourceSource("/application.yml", optional = true)
        .build()
        .loadConfigOrThrow<Config>()
}

fun repo(repo: RepositoryConfig): FocusableRepository {
    if (repo.inmemory) return null!!
    return PostgresFocusableRepository(database(repo.datasource!!))
}

fun main() {
    val config = config()

    val repo: FocusableRepository = repo(config.repo)

    val analyser = DefaultFocusableAnalyser(repo)
    val actionDefiner = DefaultActionDefiner(repo)
    val giver = DefaultAttentionGiver(repo)
    val focusableDefiner = DefaultFocusableDefiner(repo)
    val formatter = DefaultFocusableFormatter(config.format.columns)

    val db = FocusObserverDB("observer")
    val bot = FocusObserverBot(
        config.telegram,
        db,
        actionDefiner,
        focusableDefiner,
        analyser,
        giver,
        formatter
    )

    val console = TelegramBotConsole(bot)

    console.start()
}