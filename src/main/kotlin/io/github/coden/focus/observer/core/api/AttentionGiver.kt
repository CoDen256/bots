package io.github.coden.focus.observer.core.api

import java.time.Instant

interface AttentionGiver {
    fun add(request: NewAttentionRequest): Result<NewAttentionResponse>
    fun delete(request: DeleteAttentionRequest): Result<DeleteAttentionResponse>
    fun deleteLast(request: DeleteLastAttentionRequest): Result<DeleteLastAttentionResponse>
    fun clear(request: ClearAttentionsRequest): Result<ClearAttentionsResponse>
}


sealed interface AttentionGiverRequest

data class NewAttentionRequest(val timestamp: Instant, val focusId: String, val actionId: Int): AttentionGiverRequest
data class DeleteAttentionRequest(val timestamp: Instant, val focusId: String): AttentionGiverRequest
data class DeleteLastAttentionRequest(val focusId: String): AttentionGiverRequest
data object ClearAttentionsRequest: AttentionGiverRequest


sealed interface AttentionGiverResponse

data class NewAttentionResponse(val timestamp: Instant, val focusId: String, val actionId: Int): AttentionGiverResponse
data class DeleteAttentionResponse(val timestamp: Instant, val focusId: String): AttentionGiverResponse
data class DeleteLastAttentionResponse(val focusId: String): AttentionGiverResponse
data class ClearAttentionsResponse(val count: Long): AttentionGiverResponse