package io.github.coden256.focus.core.impl

import io.github.coden256.focus.core.api.*
import io.github.coden256.focus.core.model.Action
import io.github.coden256.focus.core.model.ActionId
import io.github.coden256.focus.core.model.FocusableRepository
import io.github.coden256.utils.flatMap
import io.github.coden256.utils.log
import org.apache.logging.log4j.kotlin.Logging

class DefaultActionDefiner(
    private val repo: FocusableRepository
) : ActionDefiner, Logging {
    override fun add(request: NewActionRequest): Result<NewActionResponse> {
        logger.info("Adding new action: ${request.name}")

        return repo.getNextActionId()
            .flatMap { repo.saveAction(Action(it, request.name)) }
            .map { NewActionResponse(it.id.value, it.type) }
            .log(logger) { "Added new action: ${it.id}" }
    }

    override fun delete(request: DeleteActionRequest): Result<DeleteActionResponse> {
        logger.info("Deleting action: ${request.id}")

        return repo.deleteAction(ActionId(request.id))
            .map { DeleteActionResponse(it.id.value) }
            .log(logger) { "Deleted action: ${request.id}" }
    }

    override fun update(request: UpdateActionRequest): Result<UpdateActionResponse> {
        logger.info("Updating action: ${request.id} -> ${request.name}")

        return repo
            .updateAction(Action(ActionId(request.id), request.name))
            .map { UpdateActionResponse(it.id.value, it.type) }
            .log(logger) { "Updated action: ${request.id}" }
    }

    override fun clear(request: ClearActionsRequest): Result<ClearActionsResponse> {
        logger.info("Clearing actions")
        return repo
            .clearActions()
            .map { ClearActionsResponse(it) }
            .log(logger) { "Cleared ${it.count} actions" }
    }
}