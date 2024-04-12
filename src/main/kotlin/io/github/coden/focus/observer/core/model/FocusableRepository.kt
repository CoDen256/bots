package io.github.coden.focus.observer.core.model

import java.sql.Timestamp

interface FocusableRepository{
    fun saveFocusable(focusable: Focusable): Result<Focusable>
    fun saveAction(action: Action): Result<Action>
    fun saveAttentionInstant(attentionInstant: AttentionInstant): Result<AttentionInstant>

    fun deleteFocusable(focusableId: FocusableId): Result<Focusable>
    fun deleteAction(actionId: ActionId): Result<Action>
    fun deleteAttentionInstant(focusableId: FocusableId, timestamp: Timestamp): Result<AttentionInstant>
    fun deleteLastAttentionInstant(focusableId: FocusableId): Result<AttentionInstant>

    fun update(focusable: Focusable): Result<Focusable>
    fun update(action: Action): Result<Action>

    fun clearFocusables(): Result<Long>
    fun clearActions(): Result<Long>
    fun clearAttentionInstants(): Result<Long>

    fun getNextFocusableId(): Result<FocusableId>
    fun getNextActionId(): Result<ActionId>

    fun getFocusableById(id: FocusableId): Result<Focusable>
    fun getActionById(id: ActionId): Result<Action>
    fun getAttentionInstantById(focusableId: FocusableId, timestamp: Timestamp): Result<AttentionInstant>
    fun getLastAttentionInstant(focusableId: FocusableId): Result<AttentionInstant>

    fun getFocusableAttentionTimeline(focusableId: FocusableId): Result<FocusableAttentionTimeline>
    fun getFocusableAttentionTimelines(): Result<List<FocusableAttentionTimeline>>
}