package io.github.coden.focus.observer.telegram

import io.github.coden.focus.observer.core.api.*
import io.github.coden.focus.observer.telegram.commands.*
import io.github.coden.focus.observer.telegram.format.FocusableFormatter
import io.github.coden.telegram.abilities.*
import io.github.coden.telegram.db.BotMessage
import io.github.coden.telegram.db.BotMessage.Companion.asBot
import io.github.coden.telegram.db.Chat
import io.github.coden.telegram.db.OwnerMessage.Companion.asOwner
import io.github.coden.telegram.keyboard.KeyboardButton
import io.github.coden.telegram.keyboard.keyboard
import io.github.coden.telegram.senders.deleteMessage
import io.github.coden.telegram.senders.edit
import io.github.coden.telegram.senders.editBuilder
import io.github.coden.telegram.senders.send
import org.telegram.abilitybots.api.objects.Flag
import org.telegram.abilitybots.api.objects.Reply
import org.telegram.telegrambots.meta.api.objects.Update
import java.time.Instant

class FocusObserverBot(
    config: TelegramBotConfig,
    db: FocusObserverDB,
    private val actionDefiner: ActionDefiner,
    private val focusableDefiner: FocusableableDefiner,
    private val analyser: FocusableAnalyser,
    private val attentionGiver: AttentionGiver,
    private val formatter: FocusableFormatter
) : BaseTelegramBot<FocusObserverDB>(config, db) {

    private val serializer = commandSerializer<FocusObserverCommand>()

    override fun debugUpdates(): List<Update> {
        return listOf(
//            messageUpdate("/action ${randomPronouncable(4, 6)}"),
//            messageUpdate("/actions"),
//            callbackUpdate(serializer.serialize(ActivateActionCommand("1", "3"))),
//            callbackUpdate(serializer.serialize(DeleteActionCommand("2")))
        )
    }

    fun onNewAction() = ability("action") { update ->
        val name = cleanText(update)

        val response = actionDefiner.add(NewActionRequest(name)).getOrThrow()

        sender.send(formatter.newAction(response), update.chat())
    }


    fun onAllActions() = ability("actions") { upd ->
        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        val keyboard = keyboard(actions, 4) { action ->
            KeyboardButton(
                action.action,
                data = serializer.serialize(DeleteActionCommand(action.actionId))
            )
        }.getOrThrow()

        sender.send(formatter.listActions(actions), upd.chat(), keyboard)
    }

    fun onFocusableId(): Reply = replyOn({ isId(it)}) { upd ->

        val id = getId(upd).getOrThrow()
        val focusable = analyser.focusable(GetFocusableRequest(id)).getOrThrow()

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        val keyboard = keyboard(actions, 4) { action ->
            KeyboardButton(
                action.action,
                data = serializer.serialize(ActivateActionCommand(action.actionId, focusable.focusableId))
            )
        }.getOrThrow()

        val owner = db().getOwnerMessageByFocusable(focusable.focusableId).getOrNull()

        sender.send(
            formatter.focusable(focusable.focusableId, focusable.description, focusable.created),
            upd.chat(),
            keyboard,
            owner)
    }

    fun onNewFocusable() = replyOn({ isJustText(it) }) { upd ->
        val description = cleanText(upd)

        val newFocusable = focusableDefiner
            .add(NewFocusableRequest(description))
            .getOrThrow()

        sender.send(formatter.addedNewFocusable(newFocusable), upd.chat())

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }
        val keyboard = keyboard(actions, 4) { action ->
            KeyboardButton(
                action.action,
                data = serializer.serialize(ActivateActionCommand(action.actionId, newFocusable.id))
            )
        }.getOrThrow()
        val botMessage = sender.send(
            formatter.focusable(newFocusable.id, newFocusable.description, newFocusable.created),
            upd.chat(),
            keyboard
        )
        val owner = upd.message.asOwner()
        db().addFocusableToMessagesLink(newFocusable.id, owner, botMessage)
    }


    fun onEditedFocusable() = replyOn(Flag.EDITED_MESSAGE) { upd ->
        val id = db()
            .getFocusableByOwnerMessage(upd.message.asOwner())
            .getOrThrow()

        focusableDefiner.update(UpdateFocusableRequest(id, cleanText(upd)))

        syncFocusableMessages(id, upd.chat())
    }

    fun onDeletedFocusable(): Reply = replyOnReaction("\uD83D\uDC4E") { upd ->
        val id = db()
            .getFocusableByBotMessage(upd.messageReaction.messageId.asBot())
            .getOrThrow()

        val deleted = focusableDefiner.delete(DeleteFocusableRequest(id)).getOrThrow()

        syncFocusableMessages(deleted.id, upd.chat(), true)
    }




    fun onCallback() = serializer.replyOnCallbackCommand { upd, cmd ->
        when (cmd) {
            is ActivateActionCommand -> onActivatedAction(upd, cmd.actionId, cmd.focusableId)
            is DeleteActionCommand -> onDeletedAction(upd, cmd.actionId)
            is DeleteMessageCommand -> onDeletedMessage(upd)
        }
    }

    private fun onActivatedAction(upd: Update, actionId: Int, focusableId: String) {

        attentionGiver.add(
            NewAttentionRequest(
                Instant.now(),
                focusableId, actionId
            )
        ).getOrThrow()

        sender.send(formatter.actionActivated(actionId, focusableId), upd.chat())
    }

    private fun onDeletedAction(upd: Update, actionId: Int) {
        val response = actionDefiner
            .delete(DeleteActionRequest(actionId))
            .getOrThrow()

        sender.send(formatter.actionDeleted(actionId), upd.chat())
    }

    private fun onDeletedMessage(update: Update){
        val focusableId = db()
            .getFocusableByBotMessage(update.callbackQuery.message.asBot())
            .getOrThrow()

        val targets = db().getBotMessagesByFocusable(focusableId)
        db().deleteLinks(focusableId)

        for (target in targets) {
            sender.deleteMessage(target, update.chat())
        }
    }

    fun syncFocusableMessages(focusableId: String, upd: Chat, deleted: Boolean = false){
        val targets = db().getBotMessagesByFocusable(focusableId)

        if (deleted){
            return markDeleted(focusableId, upd, targets)
        }

        val focusable = analyser.focusable(GetFocusableRequest(focusableId))
            .getOrNull()
            ?: return markDeleted(focusableId, upd, targets)

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        val keyboard = keyboard(actions, 4) { action ->
            KeyboardButton(
                action.action,
                data = serializer.serialize(ActivateActionCommand(action.actionId, focusableId))
            )
        }.getOrThrow()
        val text = formatter.focusable(focusable.focusableId, focusable.description, focusable.created)

        val edit = sender.editBuilder(text, upd, keyboard)

        for (target in targets.sortedByDescending { it.id }) {
            sender.execute(edit.messageId(target.id).build())
        }
    }

    val DELETE_MESSAGE = KeyboardButton("\uD83D\uDC80 Delete",
        serializer.serialize(DeleteMessageCommand)
    )
    private fun markDeleted(
        focusableId: String,
        chat: Chat,
        targets: Set<BotMessage>
    ) {
        for (target in targets.sortedByDescending { it.id }) {
            sender.edit(
                formatter.deletedFocusable(focusableId),
                chat,
                target,
                keyboard {
                    row { b(DELETE_MESSAGE) }
                }
            )
        }
    }

}