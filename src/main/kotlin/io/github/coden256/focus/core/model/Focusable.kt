package io.github.coden256.focus.core.model

import java.time.Instant

@JvmInline
value class FocusableId(val value: String)

data class Focusable(
    val id: FocusableId,
    val description: String,
    val created: Instant = Instant.now()
)