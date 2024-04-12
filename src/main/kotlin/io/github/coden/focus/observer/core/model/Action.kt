package io.github.coden.focus.observer.core.model

@JvmInline
value class ActionId(val value: String)

/**
 * The type of attention given, an action performed in regard of a focusable.
 * - Think (I have to start, I have to stop, I have to refuse)
 * - Do (start doing, stop doing, refuse doing)
 * - Want (do want, don't want)
 * - ...
 */
data class Action(
    val id: ActionId,
    val type: String
)