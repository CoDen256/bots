package io.github.coden.focus.observer.telegram.format

import io.github.coden.focus.observer.core.api.ActionEntityResponse
import io.github.coden.focus.observer.core.api.FocusableEntityResponse
import io.github.coden.focus.observer.core.api.NewActionResponse
import io.github.coden.focus.observer.core.api.NewFocusableResponse
import io.github.coden.telegram.senders.ParseMode
import io.github.coden.telegram.senders.StyledString
import io.github.coden.telegram.senders.snippet
import io.github.coden.telegram.senders.styled
import java.time.Instant

class DefaultFocusableFormatter
    (private val actionColumns: Int)
    : FocusableFormatter {
    override fun addedNewFocusable(response: NewFocusableResponse): StyledString {
        return "Gotcha! Added new focusable #${response.id}".styled()
    }

    override fun actionActivated(actionId: Int, focusableId: String): StyledString {
        return "Action ($actionId) for $focusableId was activated".styled()
    }

    override fun actionDeleted(actionId: Int): StyledString {
        return "Action $actionId deleted".styled()
    }

    override fun focusable(id: String, description: String, created: Instant, actions: List<String>): StyledString {
        val size = actions.size
        return "*Focusable* `#${id}`".styled(ParseMode.MARKDOWN) +
               "\n${created} - ${size} actions${actions.getOrNull(0)?.let { " : $it" } ?: ""}" +
               "\n\n${description}"
    }

    override fun deletedFocusable(focusableId: String): StyledString {
        return "*Focusalbe* `#${focusableId}` - `❌REMOVED`".styled(ParseMode.MARKDOWN)
    }

    override fun listActions(actions: List<ActionEntityResponse>): StyledString {
        return "List of all actions".styled()
    }

    override fun newAction(response: NewActionResponse): StyledString {
        return "New action ${response.id} added".styled()
    }

    override fun format(focusables: List<FocusableEntityResponse>): StyledString {
        return focusables.asList("\n") { f ->
            append(
                ("${f.focusableId}\n${f.description}"
                    .take(73)
                    .strip() + "..")
                    .snippet(ParseMode.MARKDOWN))
        }
    }

    override fun keyboardActionColumns(): Int {
        return actionColumns
    }

    private fun List<FocusableEntityResponse>.asList(separator: String, formatter: StringBuilder.(FocusableEntityResponse) -> Unit): StyledString {
        val result = StringBuilder()
        for (focusable in sortedBy { it.created }) {
            formatter.invoke(result, focusable)
            result.append(separator)
        }
        result.dropLast(separator.length)
        return result.toString().styled(ParseMode.MARKDOWN)
    }
}