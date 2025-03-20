package coden.journal.core

import java.io.Closeable

interface Trigger: Closeable {
    fun start()
}

object Never: Trigger {
    override fun start() {}
    override fun close() {}
}