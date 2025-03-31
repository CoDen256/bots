package io.github.coden256.focus.core.model

import java.time.Instant


data class FocusableAttentionTimeline(
    val focusable: io.github.coden256.focus.core.model.Focusable,
    val attentionInstants: List<io.github.coden256.focus.core.model.DetailedAttentionInstant>,
)

data class DetailedAttentionInstant(val timestamp: Instant, val action: io.github.coden256.focus.core.model.Action)
