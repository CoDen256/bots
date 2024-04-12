package io.github.coden.focus.observer

import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addFileSource
import io.github.coden.database.DatasourceConfig
import io.github.coden.focus.observer.core.impl.DefaultActionDefiner
import io.github.coden.focus.observer.core.impl.DefaultFocusableAnalyser
import io.github.coden.focus.observer.core.impl.DefaultFocusableDefiner
import io.github.coden.focus.observer.core.model.FocusableRepository
import io.github.coden.telegram.abilities.TelegramBotConfig


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

fun main() {
    val config = config()
    val repo: FocusableRepository = null!!

    val analyser = DefaultFocusableAnalyser(repo)
    val actionDefiner = DefaultActionDefiner(repo)
    val giver = DefaultFocusableAnalyser(repo)
    val focusableDefiner = DefaultFocusableDefiner(repo)



    println(config)
}