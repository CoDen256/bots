package io.github.coden.focus.observer.telegram.commands


sealed interface FocusObserverCommand : CallbackCommand


class DeleteActionCommand(
    val actionId: Int,
) : FocusObserverCommand


data class ActivateActionCommand(
    val actionId: Int,
    val focusableId: String
) : FocusObserverCommand