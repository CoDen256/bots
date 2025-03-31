package io.github.coden256.focus.postgres

import io.github.coden256.database.DatasourceConfig

data class RepositoryConfig(
    val inmemory: Boolean = true,
    val datasource: DatasourceConfig?
)