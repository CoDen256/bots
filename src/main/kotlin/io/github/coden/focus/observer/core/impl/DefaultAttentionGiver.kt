package io.github.coden.focus.observer.core.impl

import io.github.coden.focus.observer.core.api.*
import io.github.coden.focus.observer.core.model.ActionId
import io.github.coden.focus.observer.core.model.AttentionInstant
import io.github.coden.focus.observer.core.model.FocusableId
import io.github.coden.focus.observer.core.model.FocusableRepository
import org.apache.logging.log4j.kotlin.Logging

class DefaultAttentionGiver(val repo: FocusableRepository)
    :AttentionGiver, Logging{
    override fun add(request: NewAttentionRequest): Result<NewAttentionResponse> {
        return repo.saveAttentionInstant(AttentionInstant(
            request.timestamp, FocusableId( request.focusId),
            ActionId(request.actionId)
        )).map { NewAttentionResponse(it.timestamp, it.focusableId.value, it.actionId.value) }
    }

    override fun delete(request: DeleteAttentionRequest): Result<DeleteAttentionResponse> {
        return repo
            .deleteAttentionInstant(FocusableId(request.focusId), request.timestamp)
            .map { DeleteAttentionResponse(it.timestamp, it.focusableId.value) }
    }

    override fun deleteLast(request: DeleteLastAttentionRequest): Result<DeleteLastAttentionResponse> {
        return repo.deleteLastAttentionInstant(FocusableId(request.focusId))
            .map { DeleteLastAttentionResponse(it.focusableId.value) }
    }

    override fun clear(request: ClearAttentionsRequest): Result<ClearAttentionsResponse> {
        return repo.clearAttentionInstants()
            .map { ClearAttentionsResponse(it) }
    }
}