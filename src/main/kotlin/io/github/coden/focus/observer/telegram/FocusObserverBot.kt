package io.github.coden.focus.observer.telegram

import io.github.coden.focus.observer.core.api.*
import io.github.coden.focus.observer.telegram.commands.ActivateActionCommand
import io.github.coden.focus.observer.telegram.commands.DeleteActionCommand
import io.github.coden.focus.observer.telegram.commands.DeleteMessageCommand
import io.github.coden.focus.observer.telegram.commands.FocusObserverCommand
import io.github.coden.focus.observer.telegram.format.FocusableFormatter
import io.github.coden.telegram.abilities.*
import io.github.coden.telegram.commands.commandSerializer
import io.github.coden.telegram.db.BotMessage
import io.github.coden.telegram.db.BotMessage.Companion.asBot
import io.github.coden.telegram.db.Chat
import io.github.coden.telegram.db.OwnerMessage.Companion.asOwner
import io.github.coden.telegram.keyboard.KeyboardButton
import io.github.coden.telegram.keyboard.asInlineKeyboardMarkup
import io.github.coden.telegram.keyboard.keyboard
import io.github.coden.telegram.senders.deleteMessage
import io.github.coden.telegram.senders.edit
import io.github.coden.telegram.senders.editBuilder
import io.github.coden.telegram.senders.send
import io.github.coden.utils.combine
import org.telegram.abilitybots.api.objects.Flag
import org.telegram.abilitybots.api.objects.Reply
import org.telegram.telegrambots.meta.api.methods.updatingmessages.EditMessageReplyMarkup
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
) : CommandableTelegramBot<FocusObserverDB, FocusObserverCommand>(config, db, commandSerializer()) {

    override fun debugUpdates(): List<Update> {
        return listOf(
//            messageUpdate("/action ${randomPronouncable(4, 6)}"),
//            messageUpdate("/actions"),
//            callbackUpdate(serializer.serialize(ActivateActionCommand("1", "3"))),
//            callbackUpdate(serializer.serialize(DeleteActionCommand("2")))
        )
    }
    // TODO some reactive stuff?
    // focusable changed -> bla -> bla


    fun onActivatedAction() = replyOn(Flag.REPLY) { upd ->

        val action = cleanText(upd)

        val (focusableId, newAction, newAttention) = db()
            .getFocusableByBotMessage(upd.message.replyToMessage.asBot())
            .combine { actionDefiner.add(NewActionRequest(action)) }
            .combine { focusableId, newAction ->
                attentionGiver.add(NewAttentionRequest(Instant.now(), focusableId, newAction.id))
            }
            .getOrThrow()

        syncFocusableMessages(focusableId, upd.chat())
    }

    fun onNewAction() = ability("action") { update ->
        val name = cleanText(update)

        val response = actionDefiner.add(NewActionRequest(name)).getOrThrow()

        sender.send(formatter.newAction(response), update.chat())
        syncFocusableKeyboards(update.chat(), analyser.actions(ListActionsRequest).getOrThrow().actions)
    }


    fun onAllActions() = ability("actions") { upd ->
        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        val keyboard = keyboard(actions, formatter.keyboardActionColumns()) { action ->
            KeyboardButton(
                action.action,
                data = cmdSerializer.serialize(DeleteActionCommand(action.actionId))
            )
        }.getOrThrow()

        sender.send(
            formatter.listActions(actions), upd.chat(),
//            keyboard
        )
    }

    fun onAllFocusables() = ability("all") { update ->
        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }
        val response = analyser
            .focusables(ListFocusablesRequest)
            .getOrThrow()
            .focusables
            .forEach {
                sendFocusable(actions, it, update)
            }
    }

    fun onFocusables() = ability("focus") { update ->
        val response = analyser
            .focusables(ListFocusablesRequest)
            .getOrThrow()

        sender.send(formatter.format(response.focusables), update.chat())
    }

    fun onFocusableId(): Reply = replyOn({ isId(it) }) { upd ->
        val id = getId(upd).getOrThrow()
        val focusable = analyser.focusable(GetFocusableRequest(id)).getOrThrow()

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        sendFocusable(actions, focusable, upd)
    }

    private fun sendFocusable(
        actions: List<ActionEntityResponse>,
        focusable: FocusableEntityResponse,
        upd: Update
    ) {
        val keyboard = keyboard(actions, formatter.keyboardActionColumns()) { action ->
            KeyboardButton(
                action.action,
                data = cmdSerializer.serialize(ActivateActionCommand(action.actionId, focusable.focusableId))
            )
        }.getOrThrow()

        val owner = db().getOwnerMessageByFocusable(focusable.focusableId).getOrNull()
        val timeline = analyser.timeline(GetTimelineRequest(focusable.focusableId))
            .getOrNull()
        val text = formatter.focusable(
            focusable.focusableId,
            focusable.description,
            focusable.created,
            timeline?.timeline?.map { it.action.action } ?: emptyList()
        )
        val bot = sender.send(
            text,
            upd.chat(),
            replyTo = owner
        )

        db().addBotMessageLink(focusable.focusableId, bot)
    }

    fun onNewFocusable() = replyOn({ isJustText(it) && it.message?.isReply != true}) { upd ->
        val description = cleanText(upd)

        val newFocusable = focusableDefiner
            .add(NewFocusableRequest(description))
            .getOrThrow()

        sender.send(formatter.addedNewFocusable(newFocusable), upd.chat())

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }


        val keyboard = keyboard(actions, formatter.keyboardActionColumns()) { action ->
            KeyboardButton(
                action.action,
                data = cmdSerializer.serialize(ActivateActionCommand(action.actionId, newFocusable.id))
            )
        }.getOrThrow()

        val timeline = analyser.timeline(GetTimelineRequest(newFocusable.id)).getOrNull()

        val text = formatter.focusable(
            newFocusable.id,
            newFocusable.description,
            newFocusable.created,
            timeline?.timeline?.map { it.action.action } ?: emptyList()
        )

        val botMessage = sender.send(text, upd.chat())
        val owner = upd.message.asOwner()
        db().addFocusableToMessagesLink(newFocusable.id, owner, botMessage)

        syncFocusableMessages(newFocusable.id, upd.chat())
    }


    fun onEditedFocusable() = replyOn(Flag.EDITED_MESSAGE) { upd ->
        val id = db()
            .getFocusableByOwnerMessage(upd.editedMessage.asOwner())
            .getOrThrow()

        focusableDefiner
            .update(UpdateFocusableRequest(id, cleanText(upd.editedMessage)))
            .getOrThrow()

        syncFocusableMessages(id, upd.chat())
    }

    fun onDeletedFocusable(): Reply = replyOnReaction("\uD83D\uDC4E") { upd ->
        val id = db()
            .getFocusableByBotMessage(upd.messageReaction.messageId.asBot())
            .getOrThrow()

        val deleted = focusableDefiner.delete(DeleteFocusableRequest(id)).getOrThrow()

        syncFocusableMessages(deleted.id, upd.chat(), true)
    }

    override fun handleCallback(update: Update, command: FocusObserverCommand) {
        when (command) {
            is ActivateActionCommand -> onActivatedAction(update, command.actionId, command.focusableId)
            is DeleteActionCommand -> onDeletedAction(update, command.actionId)
            is DeleteMessageCommand -> onDeletedMessage(update)
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

        syncFocusableMessages(focusableId, upd.chat())
    }

    private fun onDeletedAction(upd: Update, actionId: Int) {
        val response = actionDefiner
            .delete(DeleteActionRequest(actionId))
            .getOrThrow()

        sender.send(formatter.actionDeleted(actionId), upd.chat())

        syncFocusableKeyboards(upd.chat(), analyser.actions(ListActionsRequest).getOrThrow().actions)
    }

    private fun onDeletedMessage(update: Update) {
        val focusableId = db()
            .getFocusableByBotMessage(update.callbackQuery.message.asBot())
            .getOrThrow()

        val targets = db().getBotMessagesByFocusable(focusableId)
        db().deleteLinks(focusableId)

        for (target in targets) {
            sender.deleteMessage(target, update.chat())
        }
    }


    fun syncFocusableKeyboards(chat: Chat, actions: List<ActionEntityResponse>) {

        val editReply = EditMessageReplyMarkup.builder().apply {
            chatId(chat.id)
        }
        db().getAllBotMessages().sortedByDescending { it.second.id }
            .forEach { (focusableId, botMessage) ->
                val keyboard = keyboard(actions, formatter.keyboardActionColumns()) { action ->
                    KeyboardButton(
                        action.action,
                        data = cmdSerializer.serialize(ActivateActionCommand(action.actionId, focusableId))
                    )
                }.getOrNull()
                    ?.asInlineKeyboardMarkup() ?: return@forEach

                try {
                    sender.execute(
                        editReply
//                    .replyMarkup(keyboard)
                            .messageId(botMessage.id)
                            .build()
                    )
                } catch (e: Exception) {
                    logger.error(e)
                    return@forEach
                }
            }
    }

    fun syncFocusableMessages(focusableId: String, upd: Chat, deleted: Boolean = false) {
        val targets = db().getBotMessagesByFocusable(focusableId)

        if (deleted) {
            return markDeleted(focusableId, upd, targets)
        }

        val focusable = analyser.focusable(GetFocusableRequest(focusableId))
            .getOrNull()
            ?: return markDeleted(focusableId, upd, targets)

        val actions = analyser.actions(ListActionsRequest)
            .getOrThrow()
            .actions
            .sortedBy { it.actionId }

        val keyboard = keyboard(actions, formatter.keyboardActionColumns()) { action ->
            KeyboardButton(
                action.action,
//                data = cmdSerializer.serialize(ActivateActionCommand(action.actionId, focusableId))
            )
        }.getOrThrow()


        val timeline = analyser.timeline(GetTimelineRequest(focusable.focusableId))
            .getOrNull()
        val text = formatter.focusable(
            focusable.focusableId,
            focusable.description,
            focusable.created,
            timeline?.timeline?.map { it.action.action } ?: emptyList()
        )

        val edit = sender.editBuilder(
            text, upd,
//            keyboard
        )

        for (target in targets.sortedByDescending { it.id }) {
            sender.execute(edit.messageId(target.id).build())
        }
    }

    val DELETE_MESSAGE = KeyboardButton(
        "\uD83D\uDC80 Delete",
        cmdSerializer.serialize(DeleteMessageCommand)
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