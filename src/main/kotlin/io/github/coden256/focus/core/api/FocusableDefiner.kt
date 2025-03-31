package io.github.coden256.focus.core.api

import java.time.Instant

interface FocusableableDefiner {
    fun add(request: NewFocusableRequest): Result<NewFocusableResponse>
    fun delete(request: DeleteFocusableRequest): Result<DeleteFocusableResponse>
    fun update(request: UpdateFocusableRequest): Result<UpdateFocusableResponse>
    fun clear(request: ClearFocusablesRequest): Result<ClearFocusablesResponse>
}


sealed interface FocusableDefinerRequest

data class NewFocusableRequest(val description: String): FocusableDefinerRequest
data class DeleteFocusableRequest(val id: String): FocusableDefinerRequest
data class UpdateFocusableRequest(val id: String, val description: String): FocusableDefinerRequest
data object ClearFocusablesRequest: FocusableDefinerRequest


sealed interface FocusableDefinerResponse

data class NewFocusableResponse(val id: String, val description: String, val created: Instant): FocusableDefinerResponse
data class DeleteFocusableResponse(val id: String): FocusableDefinerResponse
data class UpdateFocusableResponse(val id: String, val description: String, val created: Instant): FocusableDefinerResponse
data class ClearFocusablesResponse(val count: Long): FocusableDefinerResponse