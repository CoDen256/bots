package io.github.coden.focus.observer.core.model

import java.time.Instant


data class FocusableAttentionTimeline(
    val focusable: Focusable,
    val attentionInstants: List<DetailedAttentionInstant>,
)

data class DetailedAttentionInstant(val timestamp: Instant, val action: Action)
