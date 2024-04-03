package coden.dairy.reminder.core

interface UI {
    fun requestEntry(): Result<String>
}