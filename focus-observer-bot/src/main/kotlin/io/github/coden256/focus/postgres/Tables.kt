package io.github.coden256.focus.postgres

import org.jetbrains.exposed.sql.Table
import org.jetbrains.exposed.sql.kotlin.datetime.timestamp


object Focusables : Table("focusables") {
    val id = varchar("id", 5)
    val description = text("description")
    val created = timestamp("created")
    override val primaryKey = PrimaryKey(id)
}

object Actions : Table("focusable_actions") {
    val id = integer("id")
    val name = varchar("name", 50)
    override val primaryKey = PrimaryKey(id)
}

object AttentionInstants : Table("focus_attention_instants") {
    val timestamp = timestamp("timestamp")
    val focusableId = reference("focusable_id", Focusables.id)
    val actionId = reference("action_id", Actions.id)

    override val primaryKey = PrimaryKey(timestamp, focusableId)
}