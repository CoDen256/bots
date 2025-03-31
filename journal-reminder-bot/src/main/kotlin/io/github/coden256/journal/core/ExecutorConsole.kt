package io.github.coden256.journal.core

import java.io.Closeable

interface ExecutorConsole: Closeable {
    fun start()
    fun stop()
    override fun close() { stop() }
}