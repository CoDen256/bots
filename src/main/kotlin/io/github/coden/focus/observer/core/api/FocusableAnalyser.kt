package io.github.coden.focus.observer.core.api

import java.time.Instant


interface FocusableAnalyser {
    fun action(request: GetActionRequest): Result<ActionEntityResponse>
    fun actions(request: ListActionsRequest): Result<ListActionResponse>


    fun focusable(request: GetFocusableRequest): Result<FocusableEntityResponse>
    fun focusables(request: ListFocusablesRequest): Result<ListFocusablesResponse>

    fun timeline(request: GetTimelineRequest): Result<FocusableTimelineEntityResponse>
    fun timelines(request: ListTimelinesRequest): Result<ListTimelinesResponse>
    fun lastAttentionInstant(request: GetLastAttentionInstantRequest): Result<AttentionEntityResponse>
}

sealed interface FocusableActivityAnalyserRequest

data class GetActionRequest(val actionId: Int): FocusableActivityAnalyserRequest
data object ListActionsRequest : FocusableActivityAnalyserRequest

data class GetFocusableRequest(val focusableId: String): FocusableActivityAnalyserRequest
data object ListFocusablesRequest: FocusableActivityAnalyserRequest

data class GetLastAttentionInstantRequest(val focusableId: String): FocusableActivityAnalyserRequest
data class GetTimelineRequest(val focusableId: String): FocusableActivityAnalyserRequest
data object ListTimelinesRequest: FocusableActivityAnalyserRequest

sealed interface FocusableActivityAnalyserResponse

data class ActionEntityResponse(val actionId: Int, val action: String): FocusableActivityAnalyserResponse
data class ListActionResponse(val actions: List<ActionEntityResponse>): FocusableActivityAnalyserResponse

data class FocusableEntityResponse(val focusableId: String, val description: String, val created: Instant): FocusableActivityAnalyserResponse
data class ListFocusablesResponse(val focusables: List<FocusableEntityResponse>): FocusableActivityAnalyserResponse

data class AttentionEntityResponse(
    val timestamp: Instant,
    val action: ActionEntityResponse
)
data class FocusableTimelineEntityResponse(
    val focusable: FocusableEntityResponse,
    val timeline: List<AttentionEntityResponse>
): FocusableActivityAnalyserResponse
data class ListTimelinesResponse(val timelines: List<FocusableTimelineEntityResponse>): FocusableActivityAnalyserResponse
