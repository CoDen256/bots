package io.github.coden.focus.observer.core.impl

import io.github.coden.focus.observer.core.api.*
import io.github.coden.focus.observer.core.model.*
import org.apache.logging.log4j.kotlin.Logging

class DefaultFocusableAnalyser(val repo: FocusableRepository) : FocusableAnalyser, Logging {
    override fun action(request: GetActionRequest): Result<ActionEntityResponse> {
        return repo.getActionById(ActionId(request.actionId))
            .map { mapActionEntity(it) }
    }

    private fun mapActionEntity(action: Action): ActionEntityResponse {
        return ActionEntityResponse(action.id.value, action.type)
    }

    override fun actions(request: ListActionsRequest): Result<ListActionResponse> {
        return repo.getActions()
            .map { it.map { mapActionEntity(it) } }
            .map { ListActionResponse(it) }
    }


    override fun lastAttentionInstant(request: GetLastAttentionInstantRequest): Result<AttentionEntityResponse> {
        return repo.getLastAttentionInstant(FocusableId(request.focusableId))
            .map { mapAttention(it) }
    }

    override fun focusable(request: GetFocusableRequest): Result<FocusableEntityResponse> {
        return repo.getFocusableById(FocusableId(request.focusableId))
            .map { mapFocusable(it) }
    }

    private fun mapFocusable(f: Focusable): FocusableEntityResponse {
        return FocusableEntityResponse(f.id.value, f.description, f.created)
    }

    override fun focusables(request: ListFocusablesRequest): Result<ListFocusablesResponse> {
        return repo.getFocusables()
            .map { it.map { mapFocusable(it) } }
            .map { ListFocusablesResponse(it) }
    }

    override fun timeline(request: GetTimelineRequest): Result<FocusableTimelineEntityResponse> {
        return repo.getFocusableAttentionTimeline(FocusableId(request.focusableId))
            .map { mapTimeline(it) }
    }

    private fun mapTimeline(timeline: FocusableAttentionTimeline): FocusableTimelineEntityResponse {
        return FocusableTimelineEntityResponse(mapFocusable(timeline.focusable)
            , timeline.attentionInstants.map { mapAttention(it) }

        )
    }

    private fun mapAttention(instant: DetailedAttentionInstant): AttentionEntityResponse {
        return AttentionEntityResponse(instant.timestamp, mapActionEntity(instant.action))
    }

    override fun timelines(request: ListTimelinesRequest): Result<ListTimelinesResponse> {
        return repo.getFocusableAttentionTimelines()
            .map { it.map { mapTimeline(it) } }
            .map { ListTimelinesResponse(it) }
    }
}