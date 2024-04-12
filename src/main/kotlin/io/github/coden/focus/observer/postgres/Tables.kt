package io.github.coden.focus.observer.postgres

import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.kotlin.datetime.timestamp


object Focusables : Table("focusable") {
    val id = varchar("id", 5)
    val description = text("description")
    val created = timestamp("created")
    override val primaryKey = PrimaryKey(id)
}

object Actions : Table("actions") {
    val id = varchar("id", 5)
    val name = varchar("name", 50)
    override val primaryKey = PrimaryKey(id)
}

object AttentionInstants : Table("attention_instants") {
    val timestamp = timestamp("timestamp")
    val focusableId = reference("focusable_id", Focusables.id)
    val actionId = reference("action_id", Actions.id)

    override val primaryKey = PrimaryKey(timestamp, focusableId)
}