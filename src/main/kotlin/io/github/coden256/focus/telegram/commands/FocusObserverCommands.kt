package io.github.coden256.focus.telegram.commands

import io.github.coden256.telegram.commands.CallbackCommand


sealed interface FocusObserverCommand : CallbackCommand

class DeleteActionCommand(
    val actionId: Int,
) : FocusObserverCommand


data class ActivateActionCommand(
    val actionId: Int,
    val focusableId: String
) : FocusObserverCommand

data object DeleteMessageCommand: FocusObserverCommand