package io.github.coden.focus.observer.telegram.format

import io.github.coden.focus.observer.core.api.ActionEntityResponse
import io.github.coden.focus.observer.core.api.FocusableEntityResponse
import io.github.coden.focus.observer.core.api.NewActionResponse
import io.github.coden.focus.observer.core.api.NewFocusableResponse
import io.github.coden.telegram.senders.StyledString
import java.time.Instant

interface FocusableFormatter {
    fun addedNewFocusable(response: NewFocusableResponse): StyledString
    fun actionActivated(actionId: Int, focusableId: String): StyledString
    fun actionDeleted(actionId: Int): StyledString
    fun focusable(id: String, description: String, created: Instant, lastAction: String?): StyledString
    fun deletedFocusable(focusableId: String): StyledString
    fun listActions(actions: List<ActionEntityResponse>): StyledString
    fun newAction(response: NewActionResponse): StyledString
    fun format(focusables: List<FocusableEntityResponse>): StyledString
}