package io.github.coden.focus.observer.core.model

import java.sql.Timestamp


data class FocusableAttentionTimeline(
    val focusable: Focusable,
    val attentionInstants: List<DetailedAttentionInstant>,
)

data class DetailedAttentionInstant(val timestamp: Timestamp, val action: Action)
