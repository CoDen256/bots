package io.github.coden.focus.observer.telegram

import io.github.coden.telegram.db.BotDB
import io.github.coden.telegram.db.BotMessage
import io.github.coden.telegram.db.OwnerMessage
import io.github.coden.telegram.db.db
import io.github.coden.utils.notNullOrFailure
import org.telegram.abilitybots.api.db.MapDBContext

const val OWNER_FOCUSABLE_MESSAGES = "OWNER_FOCUSABLE_MESSAGES"
const val BOT_FOCUSABLE_MESSAGES = "BOT_FOCUSABLE_MESSAGES"

class FocusObserverDB(filename: String)
    :MapDBContext(db( filename)), BotDB  {
    private val ownerMessages
        get() = getMap<OwnerMessage, String>(OWNER_FOCUSABLE_MESSAGES)

    private val botMessages
        get() = getMap<String, MutableSet<BotMessage>>(BOT_FOCUSABLE_MESSAGES)


    fun addFocusableToMessagesLink(focusableId: String, inMessage: OwnerMessage, outMessage: BotMessage) {
        ownerMessages[inMessage] = focusableId
        botMessages.putIfAbsent(focusableId, HashSet())
        botMessages[focusableId]?.add(outMessage)
        commit()
    }

    private fun addOwnerMessageLink(focusableId: String, ownerMessage: OwnerMessage) {
        ownerMessages[ownerMessage] = focusableId
        commit()
    }

    fun addBotMessageLink(focusableId: String, botMessage: BotMessage) {
        botMessages.putIfAbsent(focusableId, HashSet())
        botMessages[focusableId]?.add(botMessage)
        commit()
    }

    fun getOwnerMessageByFocusable(focusableId: String): Result<OwnerMessage> {
        return ownerMessages
            .filterValues { it == focusableId }
            .maxByOrNull { it.key.id }
            .notNullOrFailure(IllegalArgumentException("No owner message for this focusable $focusableId"))
            .map { it.key }
    }

    fun getBotMessagesByFocusable(focusableId: String): Set<BotMessage> {
        return botMessages[focusableId] ?: emptySet()
    }

    fun getFocusableByOwnerMessage(ownerMessage: OwnerMessage): Result<String> {
        return ownerMessages[ownerMessage]
            .notNullOrFailure(IllegalArgumentException("Unable to find focusable for $ownerMessage"))
    }

    fun getFocusableByBotMessage(botMessage: BotMessage): Result<String> {
        return botMessages
            .entries
            .firstOrNull { it.value.contains(botMessage) }
            ?.key
            .notNullOrFailure(IllegalArgumentException("Unable to find focusable for $botMessage"))
    }

    fun deleteLinks(focusableId: String): Result<Unit> {
        botMessages.remove(focusableId)
        ownerMessages
            .filterValues { it == focusableId }
            .toList()
            .forEach { ownerMessages.remove(it.first) }
        commit()
        return Result.success(Unit)
    }

}