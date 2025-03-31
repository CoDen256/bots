package io.github.coden256.focus.core.impl

import io.github.coden256.focus.core.api.*
import io.github.coden256.focus.core.model.Focusable
import io.github.coden256.focus.core.model.FocusableId
import io.github.coden256.focus.core.model.FocusableRepository
import io.github.coden256.utils.flatMap
import org.apache.logging.log4j.kotlin.Logging

class DefaultFocusableDefiner (
    private val repo: FocusableRepository
) : FocusableableDefiner, Logging {
    override fun add(request: NewFocusableRequest): Result<NewFocusableResponse> {
        return repo.getNextFocusableId()
            .flatMap { repo.saveFocusable(Focusable(it, request.description)) }
            .map { NewFocusableResponse(it.id.value, it.description, it.created) }
    }

    override fun delete(request: DeleteFocusableRequest): Result<DeleteFocusableResponse> {
        return repo.deleteFocusable(FocusableId( request.id))
            .map { DeleteFocusableResponse(it.id.value) }
    }

    override fun update(request: UpdateFocusableRequest): Result<UpdateFocusableResponse> {
        return repo.updateFocusable(Focusable(FocusableId(request.id), request.description))
            .map { UpdateFocusableResponse(it.id.value, it.description, it.created) }
    }

    override fun clear(request: ClearFocusablesRequest): Result<ClearFocusablesResponse> {
        return repo.clearFocusables().map { ClearFocusablesResponse(it) }
    }
}
