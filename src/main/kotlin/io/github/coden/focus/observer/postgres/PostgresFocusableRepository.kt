package io.github.coden.focus.observer.postgres

import io.github.coden.database.asDBInstant
import io.github.coden.database.asInstant
import io.github.coden.database.transaction
import io.github.coden.focus.observer.core.model.*
import io.github.coden.utils.randomPronouncable
import org.jetbrains.exposed.sql.*
import org.jetbrains.exposed.sql.SqlExpressionBuilder.eq
import java.time.Instant

class PostgresFocusableRepository(private val db: Database): FocusableRepository {

    init {
        SchemaUtils.createMissingTablesAndColumns(Focusables, Actions, AttentionInstants)
    }

    override fun saveFocusable(focusable: Focusable): Result<Focusable> = db.transaction {
        Focusables.insert {
            it[id] = focusable.id.value
            it[created] = focusable.created.asDBInstant()
            it[description] = focusable.description
        }
        focusable
    }

    override fun saveAction(action: Action): Result<Action> = db.transaction {
        Actions.insert {
            it[id] = action.id.value
            it[name] = action.type
        }
        action
    }

    override fun saveAttentionInstant(attentionInstant: AttentionInstant): Result<AttentionInstant> = db.transaction {
        AttentionInstants.insert {
            it[actionId] = attentionInstant.actionId.value
            it[focusableId] = attentionInstant.focusableId.value
            it[timestamp] = attentionInstant.timestamp.asDBInstant()
        }
        attentionInstant
    }

    override fun deleteFocusable(focusableId: FocusableId): Result<Focusable> = db.transaction {
        val focusable = fetchFocusable(focusableId)
        Focusables.deleteWhere {
            Focusables.id eq focusableId.value
        }
        focusable
    }

    private fun fetchFocusable(focusableId: FocusableId) =
        Focusables.selectAll()
            .where { Focusables.id eq focusableId.value }
            .map { mapFocusable(it) }
            .single()

    private fun mapFocusable(row: ResultRow): Focusable {
        return Focusable(
            FocusableId(row[Focusables.id]),
            row[Focusables.description],
            row[Focusables.created].asInstant()
        )
    }

    override fun deleteAction(actionId: ActionId): Result<Action> = db.transaction {
        val action = fetchAction(actionId)
        Actions.deleteWhere {
            Actions.id eq actionId.value
        }
        action
    }

    private fun fetchAction(actionId: ActionId) =
        Actions.selectAll().where { Actions.id eq actionId.value }
            .mapNotNull { mapAction(it) }
            .single()

    private fun mapAction(row: ResultRow): Action? {
        val id = row.getOrNull(Actions.id) ?: return null
            return Action(
                ActionId(id),
                row[Actions.name]
            )
    }

    override fun deleteAttentionInstant(focusableId: FocusableId, timestamp: Instant): Result<AttentionInstant> = db.transaction {
        val instant = fetchAttentionInstant(focusableId, timestamp)
        AttentionInstants.deleteWhere {
            (AttentionInstants.focusableId eq focusableId.value) and
                    (AttentionInstants.timestamp eq timestamp.asDBInstant())
        }
        instant
    }

    private fun fetchAttentionInstant(
        focusableId: FocusableId,
        timestamp: Instant
    ) = AttentionInstants.selectAll().where {
        (AttentionInstants.focusableId eq focusableId.value) and
                (AttentionInstants.timestamp eq timestamp.asDBInstant())
    }.mapNotNull {
        mapAttentionInstant(it)
    }.single()

    private fun mapAttentionInstant(row: ResultRow): AttentionInstant? {
        val timestamp = row.getOrNull(AttentionInstants.timestamp) ?: return null
        return AttentionInstant(
            timestamp.asInstant(),
            FocusableId(row[AttentionInstants.focusableId]),
            ActionId(row[AttentionInstants.actionId])
        )
    }

    override fun deleteLastAttentionInstant(focusableId: FocusableId): Result<AttentionInstant> = db.transaction {
        val instan = fetchLastAttentionInstant(focusableId)
        AttentionInstants.deleteWhere {
            (AttentionInstants.focusableId eq focusableId.value)
                .and(AttentionInstants.timestamp eq instan.timestamp.asDBInstant())
        }
        instan
    }

    private fun fetchLastAttentionInstant(focusableId: FocusableId) = AttentionInstants.selectAll()
        .where { AttentionInstants.focusableId eq focusableId.value}
        .orderBy(AttentionInstants.timestamp, SortOrder.DESC)
        .limit(1)
        .mapNotNull { mapAttentionInstant(it) }
        .single()

    override fun updateFocusable(focusable: Focusable): Result<Focusable> = db.transaction {
        Focusables.update (
            where = {
                Focusables.id eq focusable.id.value
            }
        ){
                it[Focusables.description] = focusable.description
        }
        focusable
    }

    override fun updateAction(action: Action): Result<Action> = db.transaction {
        Actions.update({
            Actions.id eq action.id.value
        }) {
            it[Actions.name] = action.type
        }
        action
    }

    override fun clearFocusables(): Result<Long> = db.transaction {
        Focusables.deleteAll().toLong()
    }

    override fun clearActions(): Result<Long> = db.transaction {
        Actions.deleteAll().toLong()
    }

    override fun clearAttentionInstants(): Result<Long> = db.transaction {
        AttentionInstants.deleteAll().toLong()
    }

    override fun getNextFocusableId(): Result<FocusableId> = db.transaction {
        FocusableId(randomPronouncable(3,5))
    }

    override fun getNextActionId(): Result<ActionId> = db.transaction {
        val lastActionId = Actions
            .select(Actions.id)
            .orderBy(Actions.id, SortOrder.DESC)
            .limit(1)
            .single()[Actions.id]
                .toInt()
        ActionId(lastActionId + 1)
    }

    override fun getFocusables(): Result<List<Focusable>> = db.transaction {
        Focusables.selectAll()
            .map { mapFocusable(it) }
    }

    override fun getActions(): Result<List<Action>> = db.transaction {
        Actions.selectAll().mapNotNull { mapAction(it) }
    }

    override fun getFocusableById(id: FocusableId): Result<Focusable> = db.transaction {
        fetchFocusable(id)
    }

    override fun getActionById(id: ActionId): Result<Action> = db.transaction {
        fetchAction(id)
    }

    override fun getAttentionInstantById(focusableId: FocusableId, timestamp: Instant): Result<DetailedAttentionInstant> = db.transaction {
        AttentionInstants
            .leftJoin(Actions, {AttentionInstants.actionId}, {Actions.id})
            .selectAll()
            .where {
                (AttentionInstants.focusableId eq focusableId.value ).
                and (AttentionInstants.timestamp eq timestamp.asDBInstant())

            }
            .orderBy(AttentionInstants.timestamp, SortOrder.DESC)
            .limit(1)
            .mapNotNull { mapDetailedAttentionInstant(it) }
            .single()
    }

    override fun getLastAttentionInstant(focusableId: FocusableId): Result<DetailedAttentionInstant> = db.transaction {
        AttentionInstants
            .leftJoin(Actions, {AttentionInstants.actionId}, {Actions.id})
            .selectAll()
            .where { AttentionInstants.focusableId eq focusableId.value}
            .orderBy(AttentionInstants.timestamp, SortOrder.DESC)
            .limit(1)
            .mapNotNull { mapDetailedAttentionInstant(it) }
            .single()
    }

    private fun mapDetailedAttentionInstant(row: ResultRow): DetailedAttentionInstant? {
        val action = mapAction(row) ?: return null
        return DetailedAttentionInstant(
            row[AttentionInstants.timestamp].asInstant(),
            action
        )
    }

    override fun getFocusableAttentionTimeline(focusableId: FocusableId): Result<FocusableAttentionTimeline> = db.transaction {
        Focusables
            .leftJoin(AttentionInstants, { Focusables.id }, { AttentionInstants.focusableId })
            .leftJoin(Actions, { AttentionInstants.actionId }, { Actions.id })
            .selectAll()
            .where { Focusables.id eq focusableId.value }
            .map {
                Triple(mapFocusable(it) ,mapAction(it), mapAttentionInstant(it))
            }
            .groupBy { it.first }
            .map { (focusable: Focusable, aggregated: List<Triple<Focusable, Action?, AttentionInstant?>>) ->
                FocusableAttentionTimeline(focusable,
                    aggregated.mapNotNull { mapDetailedAttentionInstant(it) }
                    ) }
            .single()
    }

    private fun mapDetailedAttentionInstant(it: Triple<Focusable, Action?, AttentionInstant?>): DetailedAttentionInstant? {
        val action = it.second
        val instant = it.third
        if (action == null || instant == null) {
            return null
        }
        return DetailedAttentionInstant(instant.timestamp, action)
    }

    override fun getFocusableAttentionTimelines(): Result<List<FocusableAttentionTimeline>> = db.transaction {
        Focusables
            .leftJoin(AttentionInstants, { Focusables.id }, { AttentionInstants.focusableId })
            .leftJoin(Actions, { AttentionInstants.actionId }, { Actions.id })
            .selectAll()
            .map {
                Triple(mapFocusable(it),mapAction(it), mapAttentionInstant(it))
            }
            .groupBy { it.first }
            .map { (focusable: Focusable, aggregated: List<Triple<Focusable, Action?, AttentionInstant?>>) ->
                FocusableAttentionTimeline(focusable,
                    aggregated.mapNotNull {mapDetailedAttentionInstant(it)  }
                ) }
    }
}