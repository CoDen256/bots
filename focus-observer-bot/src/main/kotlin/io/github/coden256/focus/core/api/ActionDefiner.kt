package io.github.coden256.focus.core.api

interface ActionDefiner {
    fun add(request: NewActionRequest): Result<NewActionResponse>
    fun delete(request: DeleteActionRequest): Result<DeleteActionResponse>
    fun update(request: UpdateActionRequest): Result<UpdateActionResponse>
    fun clear(request: ClearActionsRequest): Result<ClearActionsResponse>
}


sealed interface ActionDefinerRequest

data class NewActionRequest(val name: String): ActionDefinerRequest
data class DeleteActionRequest(val id: Int): ActionDefinerRequest
data class UpdateActionRequest(val id: Int, val name: String): ActionDefinerRequest
data object ClearActionsRequest: ActionDefinerRequest


sealed interface ActionDefinerResponse

data class NewActionResponse(val id: Int, val name: String): ActionDefinerResponse
data class DeleteActionResponse(val id: Int): ActionDefinerResponse
data class UpdateActionResponse(val id: Int, val name: String): ActionDefinerResponse
data class ClearActionsResponse(val count: Long): ActionDefinerResponse


