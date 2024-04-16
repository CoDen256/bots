package io.github.coden.focus.observer.postgres

import io.github.coden.database.DatasourceConfig

data class RepositoryConfig(
    val inmemory: Boolean = true,
    val datasource: DatasourceConfig?
)