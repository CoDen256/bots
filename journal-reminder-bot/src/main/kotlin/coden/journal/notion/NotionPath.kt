package coden.journal.notion

import java.nio.file.Path
import kotlin.io.path.Path

data class NotionPath(private val absolute: String) {
    
    private val path: Path = Path(absolute)

    init {
        if (path.parent == null || path.fileName == null) {
            throw IllegalArgumentException("Notion Path cannot be root element '/'")
        }
    }

    fun path(): String {
        return path.toString()
    }

    fun title(): String {
        return path.fileName?.toString() ?: "\\"
    }

    fun parents(): List<NotionPath> {
        val parent = parent() ?: return emptyList()
        return mutableListOf(parent) + parent.parents()
    }

    fun parent(): NotionPath? {
        if (path.parent.parent == null) {
            return null
        }
        return NotionPath(path.parent.toString())
    }

    fun isTopLevel(): Boolean {
        return parents().isEmpty()
    }

    override fun equals(other: Any?): Boolean {
        if (this === other) return true
        if (other !is NotionPath) return false

        if (path != other.path) return false

        return true
    }

    override fun hashCode(): Int {
        return path.hashCode()
    }
}