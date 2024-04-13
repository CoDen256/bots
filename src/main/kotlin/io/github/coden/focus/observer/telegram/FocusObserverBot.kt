package io.github.coden.focus.observer.telegram

import io.github.coden.focus.observer.core.api.*
import io.github.coden.telegram.abilities.*
import io.github.coden.telegram.debug.callbackUpdate
import io.github.coden.telegram.debug.messageUpdate
import io.github.coden.telegram.keyboard.KeyboardButton
import io.github.coden.telegram.senders.send
import org.telegram.telegrambots.meta.api.objects.Update

class FocusObserverBot(
    config: TelegramBotConfig,
    db: FocusObserverDB,
    val actionDefiner: ActionDefiner,
    val focusableDefiner: FocusableableDefiner,
    val analyser: FocusableAnalyser,
    val attentionGiver: AttentionGiver
) : BaseTelegramBot<FocusObserverDB>(config, db) {

    override fun debugUpdates(): List<Update> {
        return listOf(
            messageUpdate("/action Wasup"),
            messageUpdate("/actions"),
            callbackUpdate("ACTION:0"),
        )
    }


    fun onNewAction() = ability("action"){ update ->
        val name = cleanText(update)

        val response = actionDefiner.add(NewActionRequest(name)).getOrThrow()

        sender.send("Action ${response.id} created", update.chat())
    }

    val ACTION_COMMAND = "ACTION"
    val COMMAND_SEPARATOR = ":"

    fun onAllActions() = ability("actions") { upd ->

        val response = analyser.actions(ListActionsRequest).getOrThrow()

        val keyboard = keyboard(response.actions, 3){ action ->
            KeyboardButton(
                action.action,
                "$ACTION_COMMAND$COMMAND_SEPARATOR${action.actionId}"
            )
        }.getOrThrow()

        sender.send("This is all your actions", upd.chat(), keyboard)

    }

    fun onCallback() = replyOnCallback{ upd, data ->
        val commandArgs = data.split(COMMAND_SEPARATOR, limit = 2)
        val command = commandArgs[0]
        when (command) {
            ACTION_COMMAND -> addAction(upd, commandArgs.getOrNull(1))
        }
    }

    private fun addAction(upd: Update, args: String?) {
        if (args.isNullOrEmpty()) throw IllegalArgumentException("Args for action command cannot be empty")
        val actionId = args

        val (id, action) = analyser.action(GetActionRequest(actionId)).getOrThrow()
        sender.send("Action $action($id) activated", upd.chat())
    }
}