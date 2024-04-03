package coden.journal.core

import java.io.Closeable

interface Console: Closeable {
    fun start()
    fun stop()
    override fun close() { stop() }
}