package io.github.coden.focus.observer.telegram

import io.github.coden.focus.observer.core.api.*
import io.github.coden.focus.observer.postgres.Focusables.id
import io.github.coden.focus.observer.telegram.commands.*
import io.github.coden.telegram.abilities.*
import io.github.coden.telegram.debug.callbackUpdate
import io.github.coden.telegram.debug.messageUpdate
import io.github.coden.telegram.keyboard.KeyboardButton
import io.github.coden.telegram.senders.send
import io.github.coden.utils.randomPronouncable
import org.telegram.telegrambots.meta.api.objects.Update

class FocusObserverBot(
    config: TelegramBotConfig,
    db: FocusObserverDB,
    val actionDefiner: ActionDefiner,
    val focusableDefiner: FocusableableDefiner,
    val analyser: FocusableAnalyser,
    val attentionGiver: AttentionGiver
) : BaseTelegramBot<FocusObserverDB>(config, db) {

    private val serializer = commandSerializer<FocusObserverCommand>()

    override fun debugUpdates(): List<Update> {
        return listOf(
            messageUpdate("/action ${randomPronouncable(4, 6)}"),
//            messageUpdate("/actions"),
//            callbackUpdate(serializer.serialize(ActivateActionCommand("1", "3"))),
//            callbackUpdate(serializer.serialize(DeleteActionCommand("2")))
        )
    }

    fun onNewAction() = ability("action"){ update ->
        val name = cleanText(update)

        val response = actionDefiner.add(NewActionRequest(name)).getOrThrow()

        sender.send("Action ${response.id} created", update.chat())
    }


    fun onAllActions() = ability("actions") { upd ->
        val response = analyser.actions(ListActionsRequest).getOrThrow()

        val keyboard = keyboard(response.actions, 3){ action ->
            val cmd = DeleteActionCommand(action.actionId)
            KeyboardButton(
                action.action,
                data = serializer.serialize(cmd)
            )
        }.getOrThrow()

        sender.send("This is all your actions", upd.chat(), keyboard)
    }

    fun onCallback() = serializer.replyOnCallbackCommand { upd, cmd ->
        when (cmd) {
            is ActivateActionCommand -> activateAction(upd, cmd.actionId, cmd.focusableId.toString())
            is DeleteActionCommand -> deleteAction(upd, cmd.actionId)
        }
    }

    private fun activateAction(upd: Update, actionId: String, focusableId: String) {

        val (id, action) = analyser.action(GetActionRequest(actionId)).getOrThrow()
        sender.send("Action $action($id) for $focusableId was activated", upd.chat())
    }

    private fun deleteAction(upd: Update, actionId: String) {
        val response = actionDefiner
            .delete(DeleteActionRequest(actionId))
            .getOrThrow()

        sender.send("Action ${response.id} deleted", upd.chat())
    }
}