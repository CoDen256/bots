package coden.journal.core.request

import java.io.Closeable

interface Trigger: Closeable {
    fun start()
}

class NullTrigger: Trigger {
    override fun start() {
    }

    override fun close() {
    }
}