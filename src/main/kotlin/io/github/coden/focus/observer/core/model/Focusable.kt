package io.github.coden.focus.observer.core.model

import java.time.Instant

@JvmInline
value class FocusableId(val value: String)

data class Focusable(
    val description: String,
    val created: Instant,
    val id: FocusableId
)