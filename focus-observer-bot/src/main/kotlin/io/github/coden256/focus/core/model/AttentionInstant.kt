package io.github.coden256.focus.core.model

import java.time.Instant

/**
 * Single timed instance of interaction with the focusable.
 * Represents an attention unit given to the focus, either in the form of a
 * physical(do) or a cognitive(think) engagement
 */
data class AttentionInstant(
    val timestamp: Instant,
    val focusableId: FocusableId,
    val actionId: ActionId
)
