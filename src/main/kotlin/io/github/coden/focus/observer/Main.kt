package io.github.coden.focus.observer

import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addFileSource
import io.github.coden.database.DatasourceConfig
import io.github.coden.database.database
import io.github.coden.focus.observer.core.impl.DefaultActionDefiner
import io.github.coden.focus.observer.core.impl.DefaultAttentionGiver
import io.github.coden.focus.observer.core.impl.DefaultFocusableAnalyser
import io.github.coden.focus.observer.core.impl.DefaultFocusableDefiner
import io.github.coden.focus.observer.core.model.FocusableRepository
import io.github.coden.focus.observer.postgres.PostgresFocusableRepository
import io.github.coden.focus.observer.telegram.FocusObserverBot
import io.github.coden.focus.observer.telegram.FocusObserverDB
import io.github.coden.focus.observer.telegram.format.DefaultFocusableFormatter
import io.github.coden.telegram.abilities.TelegramBotConfig
import io.github.coden.telegram.run.TelegramBotConsole


data class RepositoryConfig(
    val inmemory: Boolean = true,
    val datasource: DatasourceConfig?
)

data class Config(
    val telegram: TelegramBotConfig,
    val repo: RepositoryConfig
)

fun config(): Config {
    return ConfigLoaderBuilder.default()
        .addFileSource("application.yml")
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
    val formatter = DefaultFocusableFormatter()

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