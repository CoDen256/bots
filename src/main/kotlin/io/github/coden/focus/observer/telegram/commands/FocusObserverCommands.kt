package io.github.coden.focus.observer.telegram.commands


sealed interface FocusObserverCommand : CallbackCommand


class DeleteActionCommand(
    val actionId: String,
) : FocusObserverCommand


data class ActivateActionCommand(
    val actionId: String,
    val focusableId: String
) : FocusObserverCommand