package io.github.coden

import com.sksamuel.hoplite.ConfigLoaderBuilder
import com.sksamuel.hoplite.addFileSource
import io.github.coden.database.DatasourceConfig
import io.github.coden.telegram.abilities.TelegramBotConfig

data class RepositoryConfig(
    val inmemory: Boolean = true,
    val datasource: DatasourceConfig?
)

data class Config(
    val telegram: TelegramBotConfig,
    val repo: RepositoryConfig
)

fun config(): Config{
    return ConfigLoaderBuilder.default()
        .addFileSource("application.yml")
        .build()
        .loadConfigOrThrow<Config>()
}

fun main() {
    val config = config()
    println(config)
}